import { useState, useEffect, useRef } from 'react';
import { axiosClient } from '../../api/axiosClient';
import { generateInvoiceHtml, generateInvoicePDF, type InvoicePDFData } from '../../utils/invoicePdfUtils';
import { Printer, Download, MessageCircle, X, Sparkles, CheckCircle2, RotateCw } from 'lucide-react';
import toast from 'react-hot-toast';

interface InvoicePreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  invoiceId?: number | null;
  initialPdfData?: InvoicePDFData | null;
  type?: 'invoice' | 'exchange' | 'purchase';
  onAfterPrint?: () => void;
}

export default function InvoicePreviewModal({
  isOpen,
  onClose,
  invoiceId,
  initialPdfData,
  type = 'invoice',
  onAfterPrint
}: InvoicePreviewModalProps) {
  const [renderedHtml, setRenderedHtml] = useState<string>('');
  const [pdfData, setPdfData] = useState<InvoicePDFData | null>(initialPdfData || null);
  const [loading, setLoading] = useState<boolean>(true);
  const [isPrinting, setIsPrinting] = useState<boolean>(false);
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const printTriggerRef = useRef<() => void>(() => {});

  // Global Escape & Ctrl+P listener on window
  useEffect(() => {
    if (!isOpen) return;

    const handleWindowKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        e.stopPropagation();
        onClose();
        return;
      }
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'p') {
        e.preventDefault();
        e.stopPropagation();
        printTriggerRef.current();
      }
    };

    window.addEventListener('keydown', handleWindowKeyDown, true);
    return () => {
      window.removeEventListener('keydown', handleWindowKeyDown, true);
    };
  }, [isOpen, onClose]);

  // Escape & Ctrl+P listener inside the preview iframe (if focused)
  useEffect(() => {
    if (!isOpen || !renderedHtml || !iframeRef.current) return;

    let attachedDoc: Document | null = null;
    let attachedWin: Window | null = null;

    const handleFrameKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        e.stopPropagation();
        onClose();
        return;
      }
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'p') {
        e.preventDefault();
        e.stopPropagation();
        printTriggerRef.current();
      }
    };

    const detachIframeListeners = () => {
      try {
        attachedDoc?.removeEventListener('keydown', handleFrameKeyDown, true);
      } catch {}
      try {
        attachedWin?.removeEventListener('keydown', handleFrameKeyDown, true);
      } catch {}
    };

    const attachIframeEscape = () => {
      detachIframeListeners();
      try {
        const frameDoc = iframeRef.current?.contentDocument || null;
        const frameWin = iframeRef.current?.contentWindow || null;
        if (frameDoc) {
          frameDoc.addEventListener('keydown', handleFrameKeyDown, true);
          attachedDoc = frameDoc;
        }
        if (frameWin) {
          frameWin.addEventListener('keydown', handleFrameKeyDown, true);
          attachedWin = frameWin;
        }
      } catch {
        // Safe cross-origin fallback
      }
    };

    const iframe = iframeRef.current;
    iframe.addEventListener('load', attachIframeEscape);
    attachIframeEscape();

    return () => {
      iframe.removeEventListener('load', attachIframeEscape);
      detachIframeListeners();
    };
  }, [isOpen, renderedHtml, onClose]);

  useEffect(() => {
    if (!isOpen) {
      setRenderedHtml('');
      setPdfData(null);
      return;
    }

    let isMounted = true;
    setLoading(true);

    const loadDataAndHtml = async () => {
      try {
        let currentData = initialPdfData;

        if (!currentData && invoiceId) {
          const endpoint =
            type === 'purchase'
              ? `/purchases/${invoiceId}/pdf-data`
              : type === 'exchange'
              ? `/exchanges/${invoiceId}/pdf-data`
              : `/invoices/${invoiceId}/pdf-data`;

          const res = await axiosClient.get(endpoint);
          currentData = res.data;
        }

        if (!currentData) {
          throw new Error('Invoice data could not be loaded');
        }

        if (isMounted) {
          setPdfData(currentData);
        }

        const html = await generateInvoiceHtml(currentData);
        if (isMounted) {
          setRenderedHtml(html);
        }
      } catch (err: any) {
        console.error('Failed to load bill preview:', err);
        toast.error(err?.message || 'Failed to render invoice preview');
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    loadDataAndHtml();

    return () => {
      isMounted = false;
    };
  }, [isOpen, invoiceId, initialPdfData, type]);

  const invoiceNumber = pdfData?.invoice?.invoice_number || (invoiceId ? `#${invoiceId}` : 'Invoice');

  const handleDirectPrint = async () => {
    if (isPrinting) return;
    if (!renderedHtml) {
      toast.error('Print preview is not ready yet');
      return;
    }
    setIsPrinting(true);
    try {
      const electronAPI = (window as any).electronAPI;
      if (electronAPI?.printHtml) {
        const res = await electronAPI.printHtml({
          html: renderedHtml,
          title: invoiceNumber,
        });
        if (res && !res.success && res.error && res.error !== 'cancelled') {
          toast.error(`Failed to print: ${res.error}`);
        } else if (res?.success && onAfterPrint) {
          onAfterPrint();
        }
        return;
      }

      if (!iframeRef.current || !iframeRef.current.contentWindow) {
        toast.error('Print preview is not ready yet');
        return;
      }
      const frameWin = iframeRef.current.contentWindow;
      frameWin.focus();
      frameWin.print();
      if (onAfterPrint) onAfterPrint();
    } catch (e: any) {
      console.error('Print trigger error:', e);
      toast.error('Failed to open print dialog');
    } finally {
      setIsPrinting(false);
    }
  };

  printTriggerRef.current = () => {
    void handleDirectPrint();
  };

  if (!isOpen) return null;

  const handleDownloadPDF = async () => {
    if (!pdfData) return;
    const toastId = 'pdf-download';
    try {
      toast.loading('Saving PDF...', { id: toastId });
      await generateInvoicePDF(pdfData);
      toast.success('PDF saved successfully!', { id: toastId });
    } catch (e: any) {
      console.error('PDF save error:', e);
      toast.error('Failed to save PDF', { id: toastId });
    }
  };

  const handleWhatsAppShare = () => {
    if (!pdfData) return;
    const inv = pdfData.invoice || {};
    const cust = pdfData.customer || {};
    const comp = pdfData.company || {};

    const storeName = comp.name || 'Jewellery Store';
    const invNo = inv.invoice_number || `#${invoiceId}`;
    const grand = parseFloat(inv.grand_total || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 });
    const paid = parseFloat(inv.cash_received || inv.amount_paid || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 });
    const balance = parseFloat(inv.balance_amount || inv.balance_due || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 });

    const phoneRaw = String(cust.phone || cust.phone_number || '').replace(/[^0-9]/g, '');
    const phone = phoneRaw.length === 10 ? `91${phoneRaw}` : phoneRaw;

    const message = `Namaste ${cust.name || 'Grahak Ji'},%0A%0AAapka bill taiyar hai from *${storeName}*:%0A- *Bill No:* ${invNo}%0A- *Total:* Rs. ${grand}%0A- *Paid:* Rs. ${paid}%0A- *Balance Due:* Rs. ${balance}%0A%0ADhanyawad! For queries, contact: ${comp.phone || ''}`;

    const waUrl = phone ? `https://wa.me/${phone}?text=${message}` : `https://wa.me/?text=${message}`;
    window.open(waUrl, '_blank');
  };

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-black/85 animate-fadeIn cursor-pointer"
      onClick={onClose}
    >
      <div 
        className="relative w-full max-w-5xl h-[92vh] max-h-[920px] bg-zinc-950 border border-zinc-800 rounded-2xl shadow-2xl flex flex-col overflow-hidden cursor-default"
        onClick={(e) => e.stopPropagation()}
      >
        
        {/* Modal Header Toolbar */}
        <div className="px-4 py-3 sm:px-6 bg-gradient-to-r from-zinc-900 via-zinc-950 to-zinc-900 border-b border-zinc-800 flex flex-wrap items-center justify-between gap-3 select-none">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-amber-500/10 border border-amber-500/20 text-amber-400 rounded-xl">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-sm sm:text-base font-bold text-zinc-100 tracking-wide">
                  Bill Print &amp; PDF Preview
                </h2>
                <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  {invoiceNumber}
                </span>
              </div>
              <p className="text-[11px] text-zinc-400">
                Visual A4 document preview ready for direct printer or digital PDF export
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2">
            <button
              onClick={handleDirectPrint}
              disabled={loading || isPrinting}
              className="flex items-center gap-1.5 px-3.5 py-2 bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-300 hover:to-amber-400 text-black rounded-xl font-bold text-xs shadow-lg shadow-amber-500/20 transition-all active:scale-95 disabled:opacity-50 cursor-pointer"
              title="Print Bill (Opens printer dialog)"
            >
              <Printer className="w-4 h-4" />
              <span>Print Bill</span>
            </button>

            <button
              onClick={handleDownloadPDF}
              disabled={loading}
              className="flex items-center gap-1.5 px-3 py-2 bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 text-zinc-200 rounded-xl font-medium text-xs transition-all active:scale-95 disabled:opacity-50 cursor-pointer"
              title="Save PDF file to computer"
            >
              <Download className="w-4 h-4 text-emerald-400" />
              <span className="hidden sm:inline">Save PDF</span>
            </button>

            <button
              onClick={handleWhatsAppShare}
              disabled={loading}
              className="flex items-center gap-1.5 px-3 py-2 bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 text-zinc-200 rounded-xl font-medium text-xs transition-all active:scale-95 disabled:opacity-50 cursor-pointer"
              title="Send bill summary on WhatsApp"
            >
              <MessageCircle className="w-4 h-4 text-emerald-400" />
              <span className="hidden sm:inline">WhatsApp</span>
            </button>

            {/* High-visibility Red EXIT Button */}
            <button
              onClick={onClose}
              className="flex items-center gap-1.5 px-3.5 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-xl font-bold text-xs shadow-lg shadow-rose-600/30 transition-all active:scale-95 cursor-pointer ml-1.5 border border-rose-500"
              title="Exit Bill Preview and Return to Billing (Esc)"
            >
              <X className="w-4 h-4 stroke-[3]" />
              <span>EXIT (Esc)</span>
            </button>
          </div>
        </div>

        {/* Modal Body / Iframe Area */}
        <div className="flex-1 bg-zinc-900/60 p-2 sm:p-4 overflow-auto flex items-center justify-center">
          {loading ? (
            <div className="flex flex-col items-center gap-3 text-zinc-400">
              <RotateCw className="w-8 h-8 text-amber-400 animate-spin" />
              <p className="text-xs font-medium text-zinc-300">Rendering high-resolution bill preview...</p>
            </div>
          ) : renderedHtml ? (
            <div className="w-full max-w-[820px] h-full bg-white rounded-lg shadow-2xl overflow-hidden border border-zinc-700 flex flex-col">
              <iframe
                ref={iframeRef}
                srcDoc={renderedHtml}
                className="w-full h-full border-0 bg-white"
                title="Invoice Print Preview"
              />
            </div>
          ) : (
            <div className="text-xs text-rose-400">Could not render bill preview.</div>
          )}
        </div>

        {/* Modal Footer Banner */}
        <div className="px-4 py-2.5 bg-zinc-950 border-t border-zinc-800/80 flex flex-wrap items-center justify-between gap-2 text-[11px] text-zinc-400">
          <div className="flex items-center gap-1.5 text-emerald-400">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Document safely saved in PC &amp; Pendrive database</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-zinc-500 font-mono text-[10px] hidden sm:inline">
              Press Esc, Ctrl+P, or click buttons
            </span>
            <button
              onClick={onClose}
              className="px-3.5 py-1.5 bg-zinc-800 hover:bg-rose-600 text-zinc-200 hover:text-white rounded-lg font-bold text-xs border border-zinc-700 hover:border-rose-500 transition-colors flex items-center gap-1.5 cursor-pointer active:scale-95"
            >
              <X className="w-3.5 h-3.5 stroke-[2.5]" />
              <span>Exit Preview / Next Bill (Esc)</span>
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
