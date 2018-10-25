from PIL import Image, ImageDraw, ImageFont
import datetime

def main(images):
  im = Image.new('RGB', (4140, 600))
  dr = ImageDraw.Draw(im)
  for i in range(0, 60):
      for j in range(0, 10):
          p = Image.open('static/images/size_original/%s.jpg'%images[j * 60 + i])
          im.paste(p,(270 + i * 60, j * 60)) 

  f1 = ImageFont.truetype('jackinput.TTF', 90)
  tx = Image.new('RGB', (600, 100))
  dr = ImageDraw.Draw(tx)
  dr.text((60, 0),'I Question', font=f1)
  r = tx.rotate(90, expand=1)
  im.paste(r, (170, 0))

  f2 = ImageFont.truetype('jackinput.TTF', 84)
  tx2 = Image.new('RGB', (600, 100))
  dr2 = ImageDraw.Draw(tx2)
  d = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
  timestring = "%d%02d%02d%02d%02d"%(d.year, d.month, d.day, d.hour, d.minute)
  dr2.text((0, 0), timestring, font=f2)
  rr = tx2.rotate(90, expand=1)
  im.paste(rr, (3870, 0))
  s = im.rotate(90, expand=1)
  #im.save('static/printtest.jpg')
  n = '%s.jpg'%(timestring + str(d.second))
  s.save('static/print_image/'+n)
  return n

