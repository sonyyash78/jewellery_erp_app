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

  if (!isOpen) return null;

  const handleDirectPrint = () => {
    if (!iframeRef.current || !iframeRef.current.contentWindow) {
      toast.error('Print preview is not ready yet');
      return;
    }
    setIsPrinting(true);
    try {
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

    const storeName = comp.name || 'Saideep Jewellers';
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

  const invoiceNumber = pdfData?.invoice?.invoice_number || (invoiceId ? `#${invoiceId}` : 'Invoice');

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-black/80 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-5xl h-[92vh] max-h-[920px] bg-zinc-950 border border-zinc-800 rounded-2xl shadow-2xl flex flex-col overflow-hidden">
        
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
              className="flex items-center gap-1.5 px-3.5 py-2 bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-300 hover:to-amber-400 text-black rounded-xl font-bold text-xs shadow-lg shadow-amber-500/20 transition-all active:scale-95 disabled:opacity-50"
              title="Print Bill (Opens printer dialog)"
            >
              <Printer className="w-4 h-4" />
              <span>Print Bill</span>
            </button>

            <button
              onClick={handleDownloadPDF}
              disabled={loading}
              className="flex items-center gap-1.5 px-3 py-2 bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 text-zinc-200 rounded-xl font-medium text-xs transition-all active:scale-95 disabled:opacity-50"
              title="Save PDF file to computer"
            >
              <Download className="w-4 h-4 text-emerald-400" />
              <span className="hidden sm:inline">Save PDF</span>
            </button>

            <button
              onClick={handleWhatsAppShare}
              disabled={loading}
              className="flex items-center gap-1.5 px-3 py-2 bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 text-zinc-200 rounded-xl font-medium text-xs transition-all active:scale-95 disabled:opacity-50"
              title="Send bill summary on WhatsApp"
            >
              <MessageCircle className="w-4 h-4 text-emerald-400" />
              <span className="hidden sm:inline">WhatsApp</span>
            </button>

            <button
              onClick={onClose}
              className="p-2 text-zinc-400 hover:text-white hover:bg-zinc-800 rounded-xl transition-colors ml-1"
              title="Close Preview (Next Customer)"
            >
              <X className="w-5 h-5" />
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
        <div className="px-4 py-2 bg-zinc-950 border-t border-zinc-800/80 flex items-center justify-between text-[11px] text-zinc-400">
          <div className="flex items-center gap-1.5 text-emerald-400">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Document safely saved in PC &amp; Pendrive database</span>
          </div>
          <span className="text-zinc-500 font-mono text-[10px]">
            Press Ctrl+P or click Print Bill above
          </span>
        </div>

      </div>
    </div>
  );
}
