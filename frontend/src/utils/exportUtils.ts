import * as XLSX from 'xlsx';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { useAuthStore } from '../store/authStore';

// Dynamic company name from active store
const getCompanyName = () => (useAuthStore.getState().user?.store_name || 'JEWELLERY STORE').toUpperCase();

export const exportToExcel = (data: any[], filename: string) => {
  const ws = XLSX.utils.json_to_sheet(data);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, "Report");
  XLSX.writeFile(wb, `${filename}.xlsx`);
};

export const exportToPDF = (data: any[], filename: string, title: string) => {
  if (data.length === 0) return;
  const doc = new jsPDF();
  
  // Header
  doc.setFontSize(18);
  doc.setTextColor(212, 175, 55); // Gold
  doc.text(getCompanyName(), 14, 22);
  
  doc.setFontSize(11);
  doc.setTextColor(100, 100, 100);
  doc.text(title, 14, 30);
  doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 36);

  const columns = Object.keys(data[0]).map(key => ({ header: key.toUpperCase(), dataKey: key }));
  
  autoTable(doc, {
    head: [columns.map(c => c.header)],
    body: data.map(row => columns.map(c => row[c.dataKey])),
    startY: 45,
    theme: 'striped',
    styles: { 
      fontSize: 9,
      cellPadding: 4,
      textColor: [40, 40, 40],
      lineColor: [220, 220, 220],
      lineWidth: 0.1,
    },
    headStyles: { 
      fillColor: [212, 175, 55], 
      textColor: [255, 255, 255],
      fontStyle: 'bold'
    },
    alternateRowStyles: { fillColor: [248, 250, 252] },
  });

  doc.save(`${filename}.pdf`);
};

/**
 * Export report summary data to PDF
 * Works with the actual backend response structure (no chart required)
 */
export const exportReportToPDF = (
  reportData: any,
  reportTitle: string,
  dateRange?: { start?: string; end?: string }
) => {
  try {
    if (!reportData) {
      throw new Error('No data provided for PDF generation');
    }

    const doc = new jsPDF();
    let yPosition = 20;

    // Company Header
    doc.setFontSize(20);
    doc.setTextColor(212, 175, 55);
    doc.text(getCompanyName(), 14, yPosition);
    yPosition += 10;

    // Report Title
    doc.setFontSize(14);
    doc.setTextColor(60, 60, 60);
    doc.text(reportTitle, 14, yPosition);
    yPosition += 8;

    // Date Range
    if (dateRange) {
      doc.setFontSize(10);
      doc.setTextColor(100, 100, 100);
      const rangeText = dateRange.start && dateRange.end 
        ? `Period: ${dateRange.start} to ${dateRange.end}`
        : 'Period: All Time';
      doc.text(rangeText, 14, yPosition);
      yPosition += 6;
    }

    // Generation Timestamp
    doc.setFontSize(9);
    doc.setTextColor(150, 150, 150);
    doc.text(`Generated: ${new Date().toLocaleString()}`, 14, yPosition);
    yPosition += 12;

    // Summary Section
    doc.setFontSize(12);
    doc.setTextColor(40, 40, 40);
    doc.text('Summary', 14, yPosition);
    yPosition += 8;

    // Prepare summary data as table
    const summaryData: any[] = [];
    
    Object.entries(reportData).forEach(([key, value]) => {
      // Skip chart data if it exists
      if (key === 'chart' || key === 'data') return;
      
      // Format the key
      const formattedKey = key
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
      
      // Format the value
      let formattedValue = String(value);
      if (typeof value === 'number') {
        // Check if it's a currency field
        if (
          key.includes('sales') || 
          key.includes('purchase') || 
          key.includes('profit') || 
          key.includes('gst') || 
          key.includes('expense') || 
          key.includes('taxable') ||
          key.includes('payable') ||
          key.includes('receivable') ||
          key.includes('cogs') ||
          key.includes('cost')
        ) {
          formattedValue = `Rs. ${value.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        } else if (key.includes('weight')) {
          formattedValue = `${value.toFixed(3)} g`;
        } else if (key.includes('margin') || key.includes('percent')) {
          formattedValue = `${value.toFixed(2)}%`;
        } else {
          formattedValue = value.toLocaleString('en-IN');
        }
      }
      
      summaryData.push([formattedKey, formattedValue]);
    });

    if (summaryData.length === 0) {
      doc.setFontSize(10);
      doc.setTextColor(150, 150, 150);
      doc.text('No data available for the selected period', 14, yPosition);
    } else {
      autoTable(doc, {
        head: [['Metric', 'Value']],
        body: summaryData,
        startY: yPosition,
        theme: 'striped',
        styles: { 
          fontSize: 10,
          cellPadding: 6,
          textColor: [40, 40, 40],
          lineColor: [220, 220, 220],
          lineWidth: 0.1,
        },
        headStyles: { 
          fillColor: [212, 175, 55], 
          textColor: [255, 255, 255],
          fontStyle: 'bold',
          halign: 'left'
        },
        alternateRowStyles: { 
          fillColor: [248, 250, 252] 
        },
        columnStyles: {
          0: { cellWidth: 80, fontStyle: 'bold', textColor: [60, 60, 60] },
          1: { cellWidth: 100, halign: 'right', textColor: [20, 20, 20] }
        }
      });
    }

    // Footer
    const pageCount = (doc as any).internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
      doc.setPage(i);
      doc.setFontSize(8);
      doc.setTextColor(150, 150, 150);
      doc.text(
        `Page ${i} of ${pageCount}`,
        doc.internal.pageSize.width / 2,
        doc.internal.pageSize.height - 10,
        { align: 'center' }
      );
    }

    // Save
    const timestamp = new Date().toISOString().split('T')[0];
    const filename = `${reportTitle.replace(/\s+/g, '_')}_${timestamp}.pdf`;
    doc.save(filename);
    
    return true;
  } catch (error) {
    console.error('Report PDF Generation Error:', error);
    throw new Error(`Failed to generate report PDF: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
};

