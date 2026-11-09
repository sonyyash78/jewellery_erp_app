import os

p = r"c:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\utils\gstInvoiceHtml.ts"
with open(p, "r", encoding="utf-8") as f:
    c = f.read()

is_crlf = "\r\n" in c
c = c.replace("\r\n", "\n")

target = """export const generateGSTInvoiceHtml = async (data: GSTInvoiceData): Promise<string> => {
  const seller = data.seller;
  const buyer = data.buyer;
  const inv = data.invoice;
  const summary = data.gst_summary;
  const einv = data.einvoice;"""

replacement = """export function toIndianWords(amount: number): string {
  const ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten',
    'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen'];
  const tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety'];

  const numToWords = (n: number): string => {
    if (n === 0) return '';
    if (n < 20) return ones[n] + ' ';
    if (n < 100) return tens[Math.floor(n / 10)] + ' ' + (n % 10 !== 0 ? ones[n % 10] + ' ' : '');
    if (n < 1000) return ones[Math.floor(n / 100)] + ' Hundred ' + numToWords(n % 100);
    if (n < 100000) return numToWords(Math.floor(n / 1000)) + 'Thousand ' + numToWords(n % 1000);
    if (n < 10000000) return numToWords(Math.floor(n / 100000)) + 'Lakh ' + numToWords(n % 100000);
    return numToWords(Math.floor(n / 10000000)) + 'Crore ' + numToWords(n % 10000000);
  };

  const rounded = Math.round(amount * 100) / 100;
  const rupees = Math.floor(rounded);
  const paise = Math.round((rounded - rupees) * 100);

  let result = 'Indian Rupees ' + (rupees === 0 ? 'Zero ' : numToWords(rupees));
  if (paise > 0) {
    result += 'and ' + numToWords(paise) + 'paise ';
  }
  return result.trim().replace(/\\s+/g, ' ') + ' Only';
}

export const generateGSTInvoiceHtml = async (data: GSTInvoiceData): Promise<string> => {
  const seller = data.seller;
  const buyer = data.buyer;
  const inv = data.invoice;
  const summary = data.gst_summary;
  const einv = data.einvoice;

  const amountWords = (summary.amount_chargeable_words && !summary.amount_chargeable_words.includes('NaN'))
    ? summary.amount_chargeable_words
    : toIndianWords(summary.grand_total);
  const taxWords = (summary.tax_amount_words && !summary.tax_amount_words.includes('NaN'))
    ? summary.tax_amount_words
    : toIndianWords(summary.total_tax_amount);"""

assert target in c, "target not found"
c = c.replace(target, replacement, 1)

c = c.replace("${summary.amount_chargeable_words}", "${amountWords}")
c = c.replace("${summary.tax_amount_words}", "${taxWords}")

final_c = c.replace("\n", "\r\n") if is_crlf else c
with open(p, "w", encoding="utf-8") as f:
    f.write(final_c)

print("Updated gstInvoiceHtml.ts successfully")
