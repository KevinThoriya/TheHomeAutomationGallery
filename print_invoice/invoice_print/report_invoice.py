from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.platypus import Table, Paragraph, Spacer, TableStyle, Image
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics


darkBlueCode = '#011E92'
darkBlue = colors.HexColor('#011E92')
darkGreenCode = 'green'
darkGreen = colors.HexColor('#5F8B1D')

pageWidth = A4[0]
pageHeight = A4[1]
showRef = False


def convert_amount_to_words(amount):
    # Dictionary to hold the number to word mappings
    num_to_words = {
        0: 'Zero', 1: 'One', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five', 6: 'Six', 7: 'Seven', 8: 'Eight', 9: 'Nine',
        10: 'Ten', 11: 'Eleven', 12: 'Twelve', 13: 'Thirteen', 14: 'Fourteen', 15: 'Fifteen', 16: 'Sixteen',
        17: 'Seventeen', 18: 'Eighteen', 19: 'Nineteen', 20: 'Twenty', 30: 'Thirty', 40: 'Forty', 50: 'Fifty',
        60: 'Sixty', 70: 'Seventy', 80: 'Eighty', 90: 'Ninety'
    }

    # Function to convert numbers less than 1000 into words
    def convert_less_than_thousand(num):
        print('num', num, type(num))
        if num < 20:
            return num_to_words[num]
        elif num < 100:
            _code = num_to_words[num // 10 * 10]
            remaining =  num % 10 
            if remaining:
                _code += '-' + num_to_words[remaining]
            return _code
        else:
            if num % 100 == 0:
                return num_to_words[num // 100] + ' Hundred'
            else:
                return num_to_words[num // 100] + ' Hundred And ' + convert_less_than_thousand(num % 100)


    def convert_less_than_lakh(num):
        if num < 1000:
            return convert_less_than_thousand(num)
        elif num < 100000:
            if num % 1000 == 0:
                return convert_less_than_thousand(num // 1000) + ' Thousand'
            else:
                return convert_less_than_thousand(num // 1000) + ' Thousand ' + convert_less_than_thousand(num % 1000)
        else:
            if num % 100000 == 0:
                return convert_less_than_thousand(num // 100000) + ' Lakh'
            else:
                return convert_less_than_thousand(num // 100000) + ' Lakh ' + convert_less_than_lakh(num % 100000)
            
    def convert_less_than_crore(num):
        if num < 100000:
            return convert_less_than_lakh(num)
        elif num < 10000000:
            if num % 100000 == 0:
                return convert_less_than_lakh(num // 100000) + ' Lakh'
            else:
                return convert_less_than_lakh(num // 100000) + ' Lakh ' + convert_less_than_lakh(num % 100000)
        else:
            if num % 10000000 == 0:
                return convert_less_than_lakh(num // 10000000) + ' Crore'
            else:
                return convert_less_than_lakh(num // 10000000) + ' Crore ' + convert_less_than_crore(num % 10000000)


    # Splitting amount into rupees and paise
    rupees, paise = map(int, amount.split('.'))
    
    # Converting rupees and paise into words
    rupees_in_words = convert_less_than_crore(rupees)
    if paise == 0:
        paise_in_words = "Zero Paise"
    else:
        paise_in_words = convert_less_than_thousand(paise) + " Paise"

    # Constructing the final result
    result = f"{rupees_in_words} Rupees and {paise_in_words}"
    return result
class Point:
    def __init__(self, pointData):
        self.x = pointData[0]
        self.y = pointData[1]

class Line:
    def __init__(self, start, end):
        self.start = Point(start)
        self.end = Point(end)

    def draw(self, canvas):
        canvas.line(self.start.x, self.start.y, self.end.x, self.end.y)

class RefRect:

    def __init__(self, start, width=0, height=0):
        self.start = Point(start)
        self.width = width
        self.height = height
    
    def draw(self, canvas):
        if showRef:
            canvas.rect(self.start.x, self.start.y, self.width, self.height, stroke=1)

import os
import hashlib
import requests

CACHE_DIR = os.path.dirname(os.path.abspath(__file__)) + '/image_cache'

def download_image(url):
    # Create cache directory if it doesn't exist
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    # Generate filename based on URL hash
    url_hash = hashlib.sha1(url.encode()).hexdigest()
    filename = os.path.join(CACHE_DIR, f'{url_hash}.jpg')

    # Download image only if it's not already cached
    if not os.path.exists(filename):
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
        else:
            print("Failed to download image")
    
    return filename

def drawBackImage(c):
    filename = download_image('https://i.pinimg.com/originals/78/af/3a/78af3a576047cb3868f7be549bc47b30.jpg')
    c.drawImage(filename, 0, 0, width=pageWidth, height=pageHeight)

def drawHeader(c, invoiceData, topStart = 0):
    textToWrite = invoiceData['companyDetail']
    paddingX = 20
    c.setFillColorRGB(0.5,0.5,0.5)
    textX = pageWidth - paddingX
    titleFontSize = textToWrite[0][1]
    textY = pageHeight - topStart - titleFontSize
    for text in textToWrite:
        fontSize = text[1]
        c.setFont("CustomFont", fontSize)
        textInterval = fontSize + 5
        c.drawRightString(textX, textY, text[0])
        textY -= textInterval
    
    Line(start=(paddingX,textY), end=(pageWidth - paddingX, textY)).draw(c)

    return textY

def container(c, invoiceData, startYPoint) :
    date_color = darkBlueCode
    endINvoiceNumberPoint = customer_invoices_number(c, invoiceData, startYPoint)
    endDatePoint = invoice_date(c, invoiceData, date_color, startYPoint=endINvoiceNumberPoint - 10)
    due_date(c, invoiceData, date_color, startYPoint=endINvoiceNumberPoint - 10)
    tableEndPoint = description_table(c,invoiceData, description_table, startYPoint=endDatePoint - 20)
    payment_communication(c, invoiceData, startYPoint=tableEndPoint - 20)
    tableEndPoint = amount_table(c, invoiceData, startYPoint=tableEndPoint - 20)  
    amount_in_words(c, invoiceData, startYPoint=tableEndPoint - 10)

def customer_invoices_number(c, invoiceData, startYPoint):
    fontSize = 20
    pdfmetrics.registerFont(TTFont("CustomFont", f'{os.path.dirname(os.path.abspath(__file__))}/oswald.ttf'))
    c.setFont("CustomFont", fontSize)  
    c.setFillColor(darkGreenCode)
    c.drawString(40,startYPoint,invoiceData['invoice']['title'])
    return startYPoint - 20

def invoice_date(c, invoiceData, date_color, startYPoint):
    if not invoiceData['invoice'].get('date'):
        return 
    fontSize = 11
    c.setFont("CustomFont-Bold", fontSize)
    c.setFillColor(date_color)
    c.drawString(40,startYPoint,"Invoice Date : ", mode=(0))
    c.setFont("CustomFont", fontSize)
    c.setFillColorRGB(0.5,0.5,0.5)
    c.drawString(40,startYPoint - fontSize - 7,invoiceData['invoice']['date'])
    return startYPoint - fontSize - 7


def due_date(c, invoiceData, date_color, startYPoint):
    if not invoiceData['invoice'].get('due_date'):
        return 
    fontSize = 11
    c.setFont("CustomFont-Bold", fontSize)
    c.setFillColor(date_color)
    c.drawString(350,startYPoint,"Due Date : ")
    c.setFont("CustomFont", fontSize)
    c.setFillColorRGB(0.5,0.5,0.5)
    c.drawString(350,startYPoint - fontSize - 7,invoiceData['invoice']['due_date'])

def description_table(c,invoiceData, description_table_color, startYPoint):
    c.setFont("CustomFont", 12)  # Set the font to use

    data = invoiceData['invoice']['items']
    rowrowHeights = [30] + [20 for i in data[1: ]]
    tableStartPoint = startYPoint - sum(rowrowHeights)
    table = Table(data, colWidths=[180, 80, 80, 100, 100], rowHeights=rowrowHeights)
    # Style
    style = TableStyle([
                        ('FONT', (0, 0), (-1, -1), 'CustomFont'),
                        ('TEXTCOLOR', (0, 0), (-1, 0), darkBlue),
                        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'CustomFont-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (5,1), (5,5), colors.fidblue),
                        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
                        
                        ])

    table.setStyle(style)

    # Add table to canvas
    table.wrapOn(c, 0, 0)
    table.drawOn(c, 40, tableStartPoint)
    return tableStartPoint

def payment_communication(c, invoiceData, startYPoint):
    if not invoiceData['invoice'].get('payment_communication'):
        return
    fontSize = 11
    startYPoint = startYPoint - 11
    c.setFont("CustomFont", fontSize)
    c.setFillColorRGB(0.5,0.5,0.5)
    c.drawString(40,startYPoint,invoiceData['invoice']['payment_communication']['title'])
    c.setFillColorRGB(0,0,0)
    c.drawString(172,startYPoint,invoiceData['invoice']['payment_communication']['value'])
    return startYPoint 

def amount_table(c, invoiceData, startYPoint):
    data = invoiceData['invoice']['amounts']
    rowHeights = [30] + [25 for i in data[1: ]]
    table = Table(data, colWidths=[200, 80], rowHeights=rowHeights)
    tableStartPoint = startYPoint - sum(rowHeights)
    totalTaxLine = len(data) - 2
    # Style
    totalIndex = len(data) - 1
    style = TableStyle([
                        
                        ('FONT', (0, 0), (-1, -1), 'CustomFont'),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
                        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),                        
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('LINEABOVE', (0, 2), (2, 2), 0, colors.white),
                        ('TEXTCOLOR', (0, 1), (2, 2), colors.gray),
                        ('TEXTCOLOR', (1, 0), (1, 0), colors.gray),
                        ('BACKGROUND', (1,totalTaxLine), (1,totalTaxLine), colors.lightgrey),
                        ('BACKGROUND', (0,totalIndex), (3,totalIndex), darkGreen),
                        ('TEXTCOLOR', (0,totalIndex), (3, totalIndex), colors.white),
                        ('TEXTCOLOR', (0, 0), (0, 0), darkGreen),
                        # ('LINEBEFORE', (1, 0), (1, 0),1, colors.white),
                        ])

    table.setStyle(style)

    # Add table to canvas
    table.wrapOn(c, 0, 0)
    table.drawOn(c, 300, tableStartPoint)
    return tableStartPoint

def amount_in_words(c, invoiceData, startYPoint):
    fontSize = 11
    startYPoint = startYPoint - 11
    c.setFont("CustomFont", fontSize)
    c.setFillColorRGB(0.5,0.5,0.5)
    c.drawRightString(pageWidth - 20,startYPoint," Total amount in words :")
    fontSize = 9
    c.setFont("CustomFont", fontSize)
    c.setFillColorRGB(0.5,0.5,0.5)
    startYPoint -= 12
    c.drawRightString(pageWidth - 20,startYPoint ,convert_amount_to_words(invoiceData['invoice']['total']))
    return startYPoint


def hello(c, invoiceData):
    c.translate(0,0)
    c.setFont("CustomFont", 14)
    c.setStrokeColorRGB(0.2,0.5,0.3)
    c.setFillColorRGB(1,0,1)

    drawBackImage(c)

    endYPoint = drawHeader(c, invoiceData, topStart=20)
    container(c, invoiceData, startYPoint=endYPoint - 50) 




demo_data = {
'companyDetail': [
    ('The Home Automation Gallery', 12), 
    ('', 1), 
    ('f-6/7, Sky Mall', 8),
    ('Morbi - 363641', 8),
    ('Gujarat, India', 8),
    ('', 1),
    ( 'www.thehomeautomationgallery.com', 8),
    ( 'thehomeautomationgallery@gmail.com', 8)],
'invoice': {
    'title': "Customer Invoices INV/2024/00001 ",
    'date': "02/10/2024",
    'due_date': "02/10/2024",
    'items': [
        ['DESCRIPTION','QUANTITY','UNIT PRICE','TAXES','AMOUNT'],
        ['pencil',' 20.00','12.00','GST 18%',' ₹ 240.00'],
        ['pencil',' 20.00','12.00','GST 18%',' ₹ 240.00'],
        ['pencil print',' 22.00','12.00','GST 18%', ' ₹ 240.00'],
    ],
    'payment_communication': {
        'title': "Payment Communication",
        'value': 'INV/2024/00001'
    },
    'amounts': [
        ['Subtotal',' ₹ 240.00 '],
        ['SGST on ₹ 240.00',' ₹ 21.60 '],
        ['CGST on ₹ 240.00',' ₹ 21.60 '],
        ['Total',' ₹ 283.20 ']
    ],
    'total': '283.20',
}
}

from io import BytesIO

def generate_pdf_content(invoiceData={}):
    # Generate PDF content
    buffer = BytesIO()
    # import pdb; pdb.set_trace();
    c = canvas.Canvas(buffer, pagesize=A4)
    pdfmetrics.registerFont(TTFont("CustomFont", f'{os.path.dirname(os.path.abspath(__file__))}/oswald.ttf'))
    pdfmetrics.registerFont(TTFont("CustomFont-Bold", f'{os.path.dirname(os.path.abspath(__file__))}/oswald-Bold.ttf'))
    hello(c, invoiceData or demo_data)
    c.save()
    pdf_content = buffer.getvalue()
    buffer.close()
    return pdf_content

def main():
    c = canvas.Canvas("hello.pdf", pagesize=A4)
    pdfmetrics.registerFont(TTFont("CustomFont", f'{os.path.dirname(os.path.abspath(__file__))}/oswald.ttf'))
    pdfmetrics.registerFont(TTFont("CustomFont-Bold", f'{os.path.dirname(os.path.abspath(__file__))}/oswald-Bold.ttf'))
    hello(c, demo_data)
    c.showPage()
    c.save()


main()