# encoding: utf-8
# https://github.com/rickyhan/macintoshplus
"""Vaporwaveは音楽のジャンルや芸術運動である[3] [4]このようなバウンスハウス、またはchillwave、そして、より広く、エレクトロニックダンスミュージック、などのインディーseapunkから2010年代初頭のダンスのジャンルに出現した。 、その態度やメッセージに多くの多様性と曖昧さ、vaporwaveがありますが：時々の両方が、大量消費社会の批判とパロディとして機能し80年代のヤッピー文化、[5]とニューエイジの音楽、音響的および審美的に彼らのノスタルジックで好奇心の魅力を紹介しながら、アーティファクト。"""
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from random import randint, choice, Random
import os, hashlib
from math import sin, cos, tan

japanese_corpus = '''それは20年前の今日だった
サージェント·ペッパーは、プレイするバンドを教え
彼らは、スタイルの外でと続いている
しかし、彼らは笑顔を上げることが保証している
だから私はあなたに導入することができる
あなたはこれらすべての年のために知られてきた行為
サージェント·ペパーズ·ロンリー·ハーツ·クラブ·バンド
私たちはしているサージェント·ペパーズ·ロンリー·ハーツ·クラブ·バンド
私たちは、あなたがショーを楽しむことを望む
私たちはしているサージェント·ペパーズ·ロンリー·ハーツ·クラブ·バンド
後ろに座ると夜を手放す
サージェント·ペッパーの孤独、サージェント·ペッパーの孤独
サージェント·ペパーズ·ロンリー·ハーツ·クラブ·バンド
それは素晴らしいですここに
それは確かにスリルだ
あなたはそのような素敵な観客だ
私たちは、私たちと一緒に家お連れしたいと思います
私たちは家に連れて行くのが大好きです
私は実際にショーを停止する必要はありません
しかし、私はあなたが「知りたいかもしれないと思った
歌手は歌を歌うために起こっていること
そして、私はあなたのすべてを一緒に歌うことを望んでいる
だから私はあなたに紹介しましょう
唯一無二のビリー·シアーズ
そして、サージェント·ペパーズ·ロンリー·ハーツ·クラブ·バンド'''.split('\n')

main_dir = str(__file__)[:17]
bubbles = [main_dir+'img/png/bubbles/' + i for i in os.listdir(main_dir+'img/png/bubbles/') if i != 'Thumbs.db']
windows = [main_dir+'img/png/windows/' + i for i in os.listdir(main_dir+'img/png/windows/') if i != 'Thumbs.db']
backgrounds = [main_dir+'img/png/background/' + i for i in os.listdir(main_dir+'img/png/background/') if i != 'Thumbs.db']
pics = [main_dir+'img/png/pics/' + i for i in os.listdir(main_dir+'img/png/pics/') if i != 'Thumbs.db']
greek = [main_dir+'img/png/greek/' + i for i in os.listdir(main_dir+'img/png/greek/') if i != 'Thumbs.db']

def random_color(k=0):
	RGB = int(k%255),int(255*cos(k)),int(255*(1-sin(k)))
	return RGB
def full_width(txt):
	'''translate to unicode letters'''
	WIDE_MAP = dict((i, i + 0xFEE0) for i in range(0x21, 0x7F))
	WIDE_MAP[0x20] = 0x3000 
	return str(txt).translate(WIDE_MAP)
def draw_text(txt, image, k=0, x=0, y=30):
	'''takes a image and places txt on it'''
	print('adding text:', txt.encode('utf-8'))
	font_path = "resources/msjhbd.ttc"
	draw = ImageDraw.Draw(image)

	#autofit
	fontsize = 1  # starting font size
	# portion of image width you want text width to be
	img_fraction = 0.50
	font = ImageFont.truetype(font_path, fontsize)
	while font.getsize(txt)[0] < img_fraction*image.size[0]*0.7:
	    # iterate until the text size is just larger than the criteria
	    fontsize += 1
	    font = ImageFont.truetype(font_path, fontsize)

	txt = full_width(txt)
	#draw.text((0, 30), txt, fill=random_color(k) , font=font)
	# #############
	# # thin border
	# draw.text((x-1, y), txt, font=font, fill=random_color(k+200))
	# draw.text((x+1, y), txt, font=font, fill=random_color(k+200))
	# draw.text((x, y-1), txt, font=font, fill=random_color(k+200))
	# draw.text((x, y+1), txt, font=font, fill=random_color(k+200))

	# thicker border
	draw.text((x-2, y-2), txt, font=font, fill=random_color(k+90))
	draw.text((x+2, y-2), txt, font=font, fill=random_color(k+60))
	draw.text((x-2, y+2), txt, font=font, fill=random_color(k+37))
	draw.text((x+2, y+2), txt, font=font, fill=random_color(k+80))
	#################


	return image

def insert_bubble(foreground_path, im):
	'''insert notification bubble on the bottom right corner'''
	print('adding bubble:', foreground_path)
	foreground = Image.open(foreground_path)
	background_size = im.size
	foreground_size = foreground.size
	im.paste(foreground, (background_size[0]-foreground_size[0], background_size[1]-foreground_size[1]), foreground)
	return im
def insert_window_as_background(foreground_path, im,k=0):
	'''fractal generative art, not a great idea for vaporwave though. not ironic enough'''
	print('adding window:', foreground_path)
	foreground = Image.open(foreground_path)
	background_size = im.size
	foreground_size = foreground.size
	ratio = float(foreground_size[0]) / float(foreground_size[1])
	for i in range(500,600,1): # the step determines the distances between 
		pos = (	int((background_size[0]-foreground_size[0])/2 + i*sin(i)/sin(k)) ,
				int((background_size[1]-foreground_size[1])/2 + i*cos(i)/ratio/cos(k))
				)
		try:
			im.paste(foreground, pos, foreground)
		except ValueError:
			im.paste(foreground, pos)
	return im
def insert_cascade(foreground_path, im, k=0, x=100,y=100):
	'''another postironic function. raster box drawing'''
	print('adding window:', foreground_path)
	foreground = Image.open(foreground_path)
	background_size = im.size
	foreground_size = foreground.size
	# ratio = float(foreground_size[0]) / float(foreground_size[1])
	acc = -1
	v = .0
	dy = .0
	for i in range(int(k*100)): # the step determines the distances between 
		dy = v * i + 0.5 * acc * (i**2)
		v = v + acc * i
		pos = (	int(x +11* i) ,
				int(y - dy)
			)
		im.paste(foreground, pos)
		if background_size[1] - foreground_size[1] <= pos[1]+foreground_size[1]:
			v = -v
			acc = acc * 0.9

	return im
def insert_window_as_background2(foreground_path, im):
	'''another postironic function. raster box drawing'''
	print('adding window:', foreground_path)
	foreground = Image.open(foreground_path)
	background_size = im.size
	foreground_size = foreground.size
	ratio = float(foreground_size[0]) / float(foreground_size[1])
	for i in range(0,100,10): # the step determines the distances between 
		pos = (	int((background_size[0]-foreground_size[0])/2 + i) ,
				int((background_size[1]-foreground_size[1])/2 - i)
				)
		im.paste(foreground, pos)
	return im
def horizon(background_path, im):
	'''stretch a picture for horizontal perspective. math is hard'''
	background = Image.open(background_path)
		# WWWWWWWWWWWWTTTTTTTTTTTTTTTTTTTFFFFFFFFFFFFFFFFFFFFFFF MATH???? :-K
	im.paste(background,(0,0))
	return im
def insert_pic(foreground_path, im, k=0, x=0, y=1000):
	'''add Vaporwaveは音楽のジャンルや芸術運動である style pic. k is for nuanced
	transformations such as rotation and oscillation'''
	print('adding pic:', foreground_path)

	foreground = Image.open(foreground_path)
	background_size = im.size
	foreground_size = foreground.size
	ratio = float(foreground_size[0]) / float(foreground_size[1])
	pos = (	x ,
			y
			)
	foreground = foreground.rotate(k*100)
	im.paste(foreground, pos, foreground)
	return im
def color(im, k=3):
	enhancer = ImageEnhance.Color(im)
	return enhancer.enhance(k)
def contrast(im, k=3):
	enhancer = ImageEnhance.Contrast(im)
	return enhancer.enhance(k)
def sharpness(im, k=3):
	enhancer = ImageEnhance.Sharpness(im)
	return enhancer.enhance(k) 
def brightness(im, k=3):
	enhancer = ImageEnhance.Brightness(im)
	return enhancer.enhance(k)
def smooth(im, k=3):
	return im.filter(ImageFilter.SMOOTH)



def hashseed(seedtext):
	return hashlib.sha224(seedtext.encode()).hexdigest()
def draw_method1(k, name, im):
	'''non-ironic function'''
	if name == 'vapor wave':
		seedvalue = str(randint(0, 999999))
	else:
		seedvalue = hashseed(name)
	x, y = size = (1000,1000)
	# im = horizon(choice(backgrounds),im)
	im = insert_cascade(Random(seedvalue+str(0)).choice(windows),im, k=0.5)
	im = insert_pic(Random(seedvalue+str(1)).choice(pics),im,k=0,x=int(x/2),y=int(y/2))
	im = insert_pic(Random(seedvalue+str(3)).choice(pics),im,k=0,x=int(x/2),y=0)
	im = insert_pic(choice(pics), im, x=randint(0, im.height), y=randint(0, im.width))
	im = insert_pic(Random(seedvalue+str(3)).choice(greek),im,k=0,x=0,y=int(y/2.5+50))
	im = insert_window_as_background(Random(seedvalue+str(7)).choice(pics), im, k=44)
	im = insert_bubble(Random(seedvalue+str(5)).choice(bubbles), im)
	im = draw_text(Random(seedvalue+str(6)).choice(japanese_corpus), im, k=500, y=int(y/2))
	im = draw_text(name, im, k=Random(seedvalue+str(13)).randint(100,500), x=50, y=int(y/2))
	im = smooth(im, Random(seedvalue+':)').randint(3,10))
	im = color(im, Random(seedvalue).randint(3,10))
	return im

if __name__ == '__main__':
	'''k is for nuanced transformations in individual functions'''
	# for k in range(100,200):
	# 	# if k!= 2: continue
	# 	print k, '------------'
	# 	im = draw_method1(float(k)/100,'MOFO NIGGER')
	# 	im.save('animated\\'+str(k)+'.png')

	############################################
	k=95
	im = draw_method1(int(k/100),name='REDDIT')
	im.save('100.png')
	print(hashseed('VAPOR MONDAY'))