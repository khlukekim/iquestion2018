from PIL import Image, ImageDraw, ImageFont

im = Image.new('RGB', (4040, 600))
dr = ImageDraw.Draw(im)
for i in range(0, 64):
    for j in range(0, 10):
        p = Image.open('static/images/size_56/%04d.jpg'%(j * 64 + i + 1))
        im.paste(p,(100 + i * 60, j * 60)) 

f = ImageFont.truetype('secrcode.ttf', 90)
tx = Image.new('RGB', (600, 100))
dr = ImageDraw.Draw(tx)
dr.text((60, 0),'I Question', font=f)
r = tx.rotate(90, expand=1)
im.paste(r, (0, 0))

tx2 = Image.new('RGB', (600, 100))
dr2 = ImageDraw.Draw(tx2)
dr2.text((20, 0), '201810122101', font=f)
rr = tx2.rotate(90, expand=1)
im.paste(rr, (3940, 0))
s = im.rotate(90, expand=1)
im.save('static/printtest.jpg')
s.save('static/printtest2.jpg')

