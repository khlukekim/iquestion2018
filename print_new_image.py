import win32print
import win32ui
from PIL import Image, ImageWin
import requests

last_file_name = ''
def main():
  while True:
    url = 'http://www.ai-question.com/check_print_status'
    response = requests.get(url=url)
    if (last_file_name == '') :
      last_file_name = response.text
    elif (last_file_name != response.text) :
      last_file_name = response.text
      with open('last_file_name', 'wb') as handle:
        response = requests.get('http://www.ai-question.com/static/print_image/' + last_file_name, stream=True)

        if not response.ok:
            print response

        for block in response.iter_content(1024):
            if not block:
                break

            handle.write(block)
      print_new_image(last_file_name)



def print_new_image(file_name):
  #
  # Constants for GetDeviceCaps
  #
  #
  # HORZRES / VERTRES = printable area
  #
  HORZRES = 8
  VERTRES = 10
  #
  # LOGPIXELS = dots per inch
  #
  LOGPIXELSX = 88
  LOGPIXELSY = 90
  #
  # PHYSICALWIDTH/HEIGHT = total area
  #
  PHYSICALWIDTH = 110
  PHYSICALHEIGHT = 111
  #
  # PHYSICALOFFSETX/Y = left / top margin
  #
  PHYSICALOFFSETX = 112
  PHYSICALOFFSETY = 113

  printer_name = win32print.GetDefaultPrinter ()

  #
  # You can only write a Device-independent bitmap
  #  directly to a Windows device context; therefore
  #  we need (for ease) to use the Python Imaging
  #  Library to manipulate the image.
  #
  # Create a device context from a named printer
  #  and assess the printable size of the paper.
  #
  hDC = win32ui.CreateDC ()
  hDC.CreatePrinterDC (printer_name)
  printable_area = hDC.GetDeviceCaps (HORZRES), hDC.GetDeviceCaps (VERTRES)
  printer_size = hDC.GetDeviceCaps (PHYSICALWIDTH), hDC.GetDeviceCaps (PHYSICALHEIGHT)
  printer_margins = hDC.GetDeviceCaps (PHYSICALOFFSETX), hDC.GetDeviceCaps (PHYSICALOFFSETY)

  #
  # Open the image, rotate it if it's wider than
  #  it is high, and work out how much to multiply
  #  each pixel by to get it as big as possible on
  #  the page without distorting.
  #
  bmp = Image.open (file_name)
  if bmp.size[0] > bmp.size[1]:
    bmp = bmp.rotate (90)

  ratios = [1.0 * printable_area[0] / bmp.size[0], 1.0 * printable_area[1] / bmp.size[1]]
  scale = min (ratios)

  #
  # Start the print job, and draw the bitmap to
  #  the printer device at the scaled size.
  #
  hDC.StartDoc (file_name)
  hDC.StartPage ()

  dib = ImageWin.Dib (bmp)
  scaled_width, scaled_height = [int (scale * i) for i in bmp.size]
  x1 = int ((printer_size[0] - scaled_width) / 2)
  y1 = int ((printer_size[1] - scaled_height) / 2)
  x2 = x1 + scaled_width
  y2 = y1 + scaled_height
  dib.draw (hDC.GetHandleOutput (), (x1, y1, x2, y2))

  hDC.EndPage ()
  hDC.EndDoc ()
  hDC.DeleteDC ()