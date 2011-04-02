#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright 2006-2009 (C) Raster Software Vigo (Sergio Costas)
# Copyright 2006-2009 (C) Peter Gill - win32 parts

# This file is part of DeVeDe
#
# DeVeDe is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# DeVeDe is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gtk
import cairo
import time
import sys
import os
import devede_executor
import devede_other

class xml_files(devede_executor.executor):
	
	""" This class creates the XML files and the menues """
	
	def __init__(self,pbar,filename,filefolder,structure,global_vars,proglabel,extcr=None):
	
		devede_executor.executor.__init__(self,filename,filefolder,pbar)
		self.proglabel=proglabel
		self.print_error=_("Failed to create the menues.")
		self.output=False
		self.structure=structure
		self.with_menu=global_vars["with_menu"]
		if (len(structure)==1) and (len(structure[0])==2) and (not self.with_menu):
			self.onlyone=True
		else:
			self.onlyone=False
		
		self.do_menu=global_vars["do_menu"]
		self.menu_bg=global_vars["menu_bg"]
		self.menu_sound=global_vars["menu_sound"]
		self.menu_sound_duration=global_vars["menu_sound_duration"]
		self.font_name=global_vars["fontname"]
		self.mplexed=True
		self.installpath=global_vars["install_path"]
		self.title_text=global_vars["menu_title_text"]
		self.title_color=global_vars["menu_title_color"]
		self.title_shadow=global_vars["menu_title_shadow"]
		self.title_fontname=global_vars["menu_title_fontname"]

		# for menu, use the same format than the global format
		self.menu_PAL=global_vars["PAL"]
		print "Menu PAL: "+str(self.menu_PAL)
		self.bgcolor=global_vars["menu_bgcolor"]
		self.fontcolor=global_vars["menu_font_color"]
		self.activecolor=global_vars["menu_selc_color"]
		self.shadowcolor=global_vars["menu_shadow_color"]
		self.inactivecolor=[65535-self.activecolor[0],65535-self.activecolor[1],65535-self.activecolor[2],self.activecolor[3]]

		self.align=global_vars["menu_alignment"]
		self.halign=global_vars["menu_halignment"]
		self.extcr=extcr
		
		self.elements_per_menu=10
		self.lines_per_menu=10
		
		counter=0
		if self.with_menu:
			self.nmenues=0
			while (len(self.structure[counter:])!=0):
				counter+=self.elements_per_menu
				self.nmenues+=1
		else:
			self.nmenues=1
		
		self.margin_x=0.1
		self.shadow_offset=0.0025
		
		self.print_error=None


	def do_menus(self):
		return self.with_menu


	def wait_end(self):
		
		if self.print_error!=None:
			return -1
		
		retval=devede_executor.executor.wait_end(self)
		if retval!=0:
			self.print_error=_("Menu generation failed.")
			return retval
		self.create_menu2(self.counter,self.nelement)
		if self.print_error!=None:
			return -1
		retval=devede_executor.executor.wait_end(self)
		if retval!=0:
			self.print_error=_("Can't add the buttons to the menus.\nIt seems a bug of SPUMUX.")
		return retval
			


	def get_elements_per_menu(self):
		
		return (self.elements_per_menu)

	
	def create_files(self):
		
		if self.create_xml():
			return _("Failed to write to the destination directory.\nCheck that you have privileges and free space there.")
	
	
	def expand_xml(self,text):
		
		text=text.replace('&','&amp;')
		text=text.replace('<','&lt;')
		text=text.replace('>','&gt;')
		text=text.replace('"','&quot;')
		text=text.replace("'",'&apos;')
		return text
	
	
	def create_xml(self):

		""" Creates the XML file for DVDAuthor """

		# calculate the position for each title
		
		title_list=[]
		counter=1
		for element in self.structure:
			title_list.append(counter)
			counter+=((len(element))-1)

		try:
			fichero=open(self.filefolder+self.filename+".xml","w")
			fichero.write('<dvdauthor dest="'+self.expand_xml(self.filefolder+self.filename)+'">\n')
			
			if self.onlyone:
				fichero.write('\t<vmgm />\n')
			else:
			
				fichero.write('\t<vmgm>\n')
				
				# MENU
				
				# in the FPC we do a jump to the first menu in the first titleset if we wanted MENU
				# or we jump to the second titleset if we didn't want MENU at startup
				
				fichero.write('\t\t<fpc>\n')
				fichero.write('\t\t\tg0=100;\n')
				if self.do_menu and self.with_menu:
					fichero.write('\t\t\tg1=0;\n')
				else:
					fichero.write('\t\t\tg1=100;\n')
				fichero.write('\t\t\tg2=1024;\n')
				fichero.write('\t\t\tjump menu 1;\n')
				fichero.write('\t\t</fpc>\n')
				
				# in the VMGM menu we create a code to jump to the title specified in G0
				# but if the title is 100, we jump to the menus. There we show the menu number
				# contained in G1
				
				fichero.write("\t\t<menus>\n")
					
				fichero.write('\t\t\t<video format="')
				if self.menu_PAL:
					fichero.write("pal")
				else:
					fichero.write("ntsc")
				fichero.write('" aspect="4:3"> </video>\n')
	
				fichero.write('\t\t\t<pgc>\n')
				fichero.write('\t\t\t\t<pre>\n')
				
				counter=1
				for element in self.structure:
					for element2 in element[1:]:
						fichero.write('\t\t\t\t\tif (g0 eq '+str(counter)+') {\n')
						fichero.write('\t\t\t\t\t\tjump titleset '+str(1+counter)+' menu;\n')
						fichero.write('\t\t\t\t\t}\n')
						counter+=1
				fichero.write('\t\t\t\t\tif (g0 eq 100) {\n')
				fichero.write('\t\t\t\t\t\tg2=1024;\n')
				fichero.write('\t\t\t\t\t\tjump titleset 1 menu;\n')
				fichero.write('\t\t\t\t\t}\n')
				fichero.write('\t\t\t\t</pre>\n')
				# fake video (one black picture with one second of sound) to ensure 100% compatibility
				fichero.write('\t\t\t\t<vob file="')
				if self.menu_PAL:
					fichero.write(self.expand_xml(str(os.path.join(self.installpath,"base_pal.mpg"))))
				else:
					fichero.write(self.expand_xml(str(os.path.join(self.installpath,"base_ntsc.mpg"))))
				fichero.write('"></vob>\n')
				fichero.write('\t\t\t</pgc>\n')
				fichero.write('\t\t</menus>\n')
				fichero.write("\t</vmgm>\n")
				
				fichero.write("\n")
				
				# the first titleset contains all the menus. G1 allows us to jump to the desired menu
				
				fichero.write('\t<titleset>\n')
				fichero.write('\t\t<menus>\n')
				fichero.write('\t\t\t<video format="')
				if self.menu_PAL:
					fichero.write("pal")
				else:
					fichero.write("ntsc")
				fichero.write('" aspect="4:3"> </video>\n')
				
				button_counter=0
				for menu_number in range(self.nmenues):
					fichero.write('\t\t\t<pgc>\n')
					fichero.write('\t\t\t\t<pre>\n')
					# first we recover the currently selected button
					fichero.write('\t\t\t\t\ts8=g2;\n')
					if menu_number==0: # here we add some code to jump to each menu
						for menu2 in range(self.nmenues-1):
							fichero.write('\t\t\t\t\tif (g1 eq '+str(menu2+1)+') {\n')
							fichero.write('\t\t\t\t\t\tjump menu '+str(menu2+2)+';\n')
							fichero.write('\t\t\t\t\t}\n')
						
						# this code is to fix a bug in some players
						fichero.write('\t\t\t\t\tif (g1 eq 100) {\n')
						fichero.write('\t\t\t\t\t\tjump title 1;\n')#menu '+str(self.nmenues+1)+';\n')
						fichero.write('\t\t\t\t\t}\n')
						
					fichero.write('\t\t\t\t</pre>\n')
					fichero.write('\t\t\t\t<vob file="')
					if self.with_menu:
						fichero.write(self.expand_xml(str(os.path.join(self.filefolder,self.filename)))+'_menu2_'+str(menu_number)+'.mpg"')
					else:
						if self.menu_PAL:
							fichero.write(self.expand_xml(str(os.path.join(self.installpath,"base_pal.mpg")))+'"')
						else:
							fichero.write(self.expand_xml(str(os.path.join(self.installpath,"base_ntsc.mpg")))+'"')
					fichero.write('></vob>\n')
					
					if self.with_menu:
						cantidad=len(self.structure[self.elements_per_menu*menu_number:(menu_number+1)*self.elements_per_menu])
						for nbutton in range(cantidad):
							fichero.write('\t\t\t\t<button name="boton')
							fichero.write(str(menu_number))
							fichero.write('x')
							fichero.write(str(nbutton))
							fichero.write('"> g0='+str(title_list[button_counter])+'; jump vmgm menu; </button>\n')
							button_counter+=1
							
						if (menu_number!=0):
							fichero.write('\t\t\t\t<button name="boton')
							fichero.write(str(menu_number))
							fichero.write('p"> g1=')
							fichero.write(str(menu_number-1))
							fichero.write('; g2=1024; jump menu ')
							fichero.write(str(menu_number))
							fichero.write('; </button>\n')
							
						if (menu_number!=self.nmenues-1) and (self.nmenues>1):
							fichero.write('\t\t\t\t<button name="boton')
							fichero.write(str(menu_number))
							fichero.write('n"> g1=')
							fichero.write(str(menu_number+1))
							fichero.write('; g2=1024; jump menu ')
							fichero.write(str(menu_number+2))
							fichero.write('; </button>\n')
					
					fichero.write('\t\t\t\t<post>\n')
					fichero.write('\t\t\t\t\tg2=s8;\n')
					fichero.write('\t\t\t\t\tg1='+str(menu_number)+';\n')
					fichero.write('\t\t\t\t\tjump menu '+str(menu_number+1)+';\n')
					fichero.write('\t\t\t\t</post>\n')
					fichero.write('\t\t\t</pgc>\n')
				
				fichero.write('\t\t</menus>\n')
				fichero.write('\t\t<titles>\n')
				fichero.write('\t\t\t<video format="')
				if self.menu_PAL:
					fichero.write("pal")
				else:
					fichero.write("ntsc")
				fichero.write('" aspect="4:3"> </video>\n')
				fichero.write('\t\t\t<pgc>\n')
				fichero.write('\t\t\t\t<vob file="')
				if self.menu_PAL:
					fichero.write(self.expand_xml(str(os.path.join(self.installpath,"base_pal.mpg"))))
				else:
					fichero.write(self.expand_xml(str(os.path.join(self.installpath,"base_ntsc.mpg"))))
				fichero.write('"></vob>\n')
				fichero.write('\t\t\t\t<post>\n')
				fichero.write('\t\t\t\t\tg0=1;\n')
				fichero.write('\t\t\t\t\tg1=0;\n')
				fichero.write('\t\t\t\t\tg2=1024;\n')
				fichero.write('\t\t\t\t\tcall vmgm menu entry title;\n')
				fichero.write('\t\t\t\t</post>\n')
				fichero.write('\t\t\t</pgc>\n')
				fichero.write('\t\t</titles>\n')
				fichero.write("\t</titleset>\n")
	
				fichero.write("\n")
				
			# Now we create the titleset for each video
			
			total_t=len(self.structure)
			titleset=1
			titles=0
			counter=0
			for element in self.structure:
				files=0
				num_chapters=len(element)-1
				action=element[0]["jumpto"]
				for element2 in element[1:]:
					fichero.write("\n")
					
					if element2["ismpeg"]:

						# if it's already an MPEG-2 compliant file, we use the original values
						if element2["ofps"]==25:
							pal_ntsc="pal"
							ispal=True
						else:
							pal_ntsc="ntsc"
							ispal=False
						if element2["oaspect"]>1.6:
							faspect='16:9'
							fwide=True
						else:
							faspect='4:3'
							fwide=False
					else:
						# but if we are converting it, we use the desired values
						if element2["fps"]==25:
							pal_ntsc="pal"
							ispal=True
						else:
							pal_ntsc="ntsc"
							ispal=False
						if element2["aspect"]>1.6:
							faspect='16:9'
							fwide=True
						else:
							faspect='4:3'
							fwide=False
					
					fichero.write("\t<titleset>\n")
					if not self.onlyone:
						fichero.write("\t\t<menus>\n")
						fichero.write('\t\t\t<video format="'+pal_ntsc+'" aspect="'+faspect+'"')
						if fwide:
							fichero.write(' widescreen="nopanscan"')
						fichero.write('> </video>\n')
						
						fichero.write("\t\t\t<pgc>\n")
						fichero.write("\t\t\t\t<pre>\n")
						fichero.write('\t\t\t\t\tif (g0 eq 100) {\n')
						fichero.write('\t\t\t\t\t\tjump vmgm menu entry title;\n')
						fichero.write('\t\t\t\t\t}\n')
						fichero.write('\t\t\t\t\tg0=100;\n')
						fichero.write('\t\t\t\t\tg1='+str(titles/self.elements_per_menu)+';\n')
						fichero.write('\t\t\t\t\tjump title 1;\n')
						fichero.write('\t\t\t\t</pre>\n')
						# fake video to ensure compatibility
						fichero.write('\t\t\t\t<vob file="')
						if ispal:
							fichero.write(self.expand_xml(str(os.path.join(self.installpath,"base_pal"))))
						else:
							fichero.write(self.expand_xml(str(os.path.join(self.installpath,"base_ntsc"))))
						if fwide:
							fichero.write("_wide")
						fichero.write('.mpg"></vob>\n')
						fichero.write("\t\t\t</pgc>\n")
						fichero.write("\t\t</menus>\n")

					fichero.write("\t\t<titles>\n")
					fichero.write('\t\t\t<video format="'+pal_ntsc+'" aspect="'+faspect+'"')
					if fwide:
						fichero.write(' widescreen="nopanscan"')
					fichero.write('> </video>\n')
					
					for element3 in element2["sub_list"]:
						fichero.write('\t\t\t<subpicture lang="'+self.expand_xml(str(element3["sub_language"][:2].lower()))+'" />\n')
					fichero.write('\t\t\t<pgc>\n')
					if (element2["force_subs"]) and (len(element2["sub_list"])!=0):
						fichero.write('\t\t\t\t<pre>\n')
						fichero.write('\t\t\t\t\tsubtitle=64;\n')
						fichero.write('\t\t\t\t</pre>\n')

					currentfile=self.create_filename(self.filefolder+self.filename,titles+1,files+1,False)
					fichero.write('\t\t\t\t<vob file="'+self.expand_xml(currentfile)+'" ')
					fichero.write('chapters="0')
					if (element2["olength"]>5):
						if (element2["lchapters"]!=0): # add chapters
							toadd=int(element2["lchapters"])
							seconds=toadd*60
							while seconds<(element2["olength"]-4):
								thetime=devede_other.return_time(seconds,False)
								fichero.write(","+thetime)
								seconds+=(toadd*60)
						fichero.write(','+devede_other.return_time((element2["olength"]-2),False))
					fichero.write('" />\n')
					
					if not self.onlyone:
						fichero.write('\t\t\t\t<post>\n')
						files+=1
						fichero.write('\t\t\t\t\tg1='+str(titles/self.elements_per_menu)+';\n')
						if (files==num_chapters) and (action=="menu"): # last chapter
							fichero.write('\t\t\t\t\tg0=100;\n')
							fichero.write('\t\t\t\t\tcall vmgm menu entry title;\n')
						else:
							fichero.write('\t\t\t\t\tg0=')
							if (files==num_chapters): # last chapter; do ACTION
								if action=="prev":
									if titles==0:
										prev_t=total_t-1
									else:
										prev_t=titles-1
									fichero.write(str(title_list[prev_t]))
								elif action=="loop":
									fichero.write(str(title_list[titles]))
								elif action=="next":
									if titles==total_t-1:
										next_t=0
									else:
										next_t=titles+1
									fichero.write(str(title_list[next_t]))
								elif action=="last":
									fichero.write(str(title_list[total_t-1]))
								else:
									fichero.write('1') # first
							else:
								 # jump to next chapter in title
								fichero.write(str(title_list[titles]+files))
							fichero.write(';\n')
							fichero.write('\t\t\t\t\tcall vmgm menu entry title;\n')
						fichero.write('\t\t\t\t</post>\n')
					fichero.write("\t\t\t</pgc>\n")
					fichero.write("\t\t</titles>\n")
					fichero.write("\t</titleset>\n")
					counter+=1
				titles+=1
			fichero.write("</dvdauthor>")
			fichero.close()
			return False
		except IOError:
			return True

	
	def create_menu1(self,counter,nelement,threads):
	
		""" Creates all the menu elements """
	
		self.threads=threads
		self.counter=counter
		self.nelement=nelement
		if self.proglabel!=None:
			self.proglabel.set_text((_("Creating menu %(menu_number)d")) % {"menu_number":nelement+1})
		print "Menu1 "+str(counter)+" "+str(nelement)
		
		# create the XML file for the menu NELEMENT
		if self.create_menu_stream(counter,nelement):
			self.print_error=_("Failed to write to the destination directory.\nCheck that you have privileges and free space there.")
			return None
		# create the background picture for the menu NELEMENT
		if None==self.create_menu_bg(counter,nelement,0):
			self.print_error=_("Can't find the menu background.\nCheck the menu options.")
			return None
		# create the ACTIVE picture for the menu NELEMENT
		if None==self.create_menu_bg(counter,nelement,1):
			self.print_error=_("Failed to write to the destination directory.\nCheck that you have privileges and free space there.")
			return None
		# create the INACTIVE picture for the menu NELEMENT
		if None==self.create_menu_bg(counter,nelement,2):
			self.print_error=_("Failed to write to the destination directory.\nCheck that you have privileges and free space there.")
			return None
		# create the SELECTED picture for the menu NELEMENT
		if None==self.create_menu_bg(counter,nelement,3):
			self.print_error=_("Failed to write to the destination directory.\nCheck that you have privileges and free space there.")
			return None
		# creates an MPEG file with the sound and the background picture
		if self.create_menu_mpg(nelement):
			self.print_error=_("Menu generation failed.")

		return None
		
	def create_menu2(self,counter,nelement):
		
		""" Mixes all files to create the NELEMENT menu MPEG file with the buttons embedded """

		if self.menu_mplex_buttons(nelement):
			self.print_error=_("Can't add the buttons to the menus.\nIt seems a bug of SPUMUX.")
			
		return None

			
	def create_menu_stream(self,first_element,nelement):

		""" Creates the menu XML file """

		cantidad=len(self.structure[first_element:first_element+self.elements_per_menu])
		if self.align!=0:
			offset=(self.lines_per_menu-cantidad)/self.align
		else:
			offset=0
			
		if self.menu_PAL:
			formato="pal"
		else:
			formato="ntsc"

		try:
			fichero=open(self.filefolder+self.filename+"_menu_"+str(nelement)+".xml","w")
			fichero.write('<subpictures>\n<stream>\n<spu force="yes" start="00:00:00.00"')# transparent="000000"')
			fichero.write(' image="'+self.expand_xml(self.filefolder+self.filename)+'_menu'+str(nelement)+'_bg_inactive_out.png"')
			fichero.write(' highlight="'+self.expand_xml(self.filefolder+self.filename)+'_menu'+str(nelement)+'_bg_active_out.png"')
			fichero.write(' select="'+self.expand_xml(self.filefolder+self.filename)+'_menu'+str(nelement)+'_bg_select_out.png" >\n')
			if self.menu_PAL:
				coord_y=[(92,128),(130,166),(168,204),(206,242),(244,280),(282,320),(322,358),(360,396),(398,436),(438,474),(476,512)]
			else:
				coord_y=[(76,106),(108,138),(140,170),(172,202),(204,234),(236,266),(268,298),(300,330),(332,362),(364,394),(396,426)]
			
			if (nelement!=0):
				has_previous=True
			else:
				has_previous=False
			
			if ((nelement!=self.nmenues-1) and (self.nmenues>1)):
				has_next=True
			else:
				has_next=False
			
			for contador in range(cantidad):
				fichero.write('<button name="boton'+str(nelement)+"x"+str(contador))
				fichero.write('" x0="0" y0="'+str(coord_y[contador+offset][0])+'" x1="719" y1="'+str(coord_y[contador+offset][1])+'"')
				if contador!=0:
					fichero.write(' up="boton'+str(nelement)+"x")
					fichero.write(str(contador-1))
					fichero.write('"')
				if contador<cantidad-1:
					fichero.write(' down="boton'+str(nelement)+"x")
					fichero.write(str(contador+1))
					fichero.write('"')
				else:
					if (nelement!=0):
						fichero.write(' down="boton'+str(nelement)+'p"')
					elif ((nelement!=self.nmenues-1) and (self.nmenues>1)):
						fichero.write(' down="boton'+str(nelement)+'n"')
				if has_next:
					fichero.write(' right="boton'+str(nelement)+'n"')
				if has_previous:
					fichero.write(' left="boton'+str(nelement)+'p"')
				fichero.write(' > </button>\n')
				
			if has_previous:
				fichero.write('<button name="boton'+str(nelement)+'p"')
				fichero.write(' x0="0" y0="'+str(coord_y[10][0])+'" x1="359" y1="'+str(coord_y[10][1])+'"')
				fichero.write(' up="boton'+str(nelement)+'x'+str(cantidad-1)+'"')
				if has_next:
					fichero.write(' right="boton'+str(nelement)+'n"')
				fichero.write(' > </button>\n')

			if has_next:
				fichero.write('<button name="boton'+str(nelement)+'n"')
				fichero.write(' x0="360" y0="'+str(coord_y[10][0])+'" x1="719" y1="'+str(coord_y[10][1])+'"')
				fichero.write(' up="boton'+str(nelement)+'x'+str(cantidad-1)+'"')
				if has_previous:
					fichero.write(' left="boton'+str(nelement)+'p"')
				fichero.write(' > </button>\n')
			fichero.write("</spu>\n</stream>\n</subpictures>\n")
			fichero.close()
			
			return False
		except IOError:
			return True
	
	
	def menu_set_bg(self,cr,x,y,width,bgcolor,fgcolor=None,shcolor=None):

		""" paints the rounded rectangles used as background for titles and buttons """

		radius=0.0375
		border=0.0048
		linea=0.0024
		# I created the button image for this size, so I must respect it :(
		#xb,yb,width,height,cx,cy=cr.text_extents("Título 1")

		height=0.0391604010025

		if width==1:
			half_button=False
		else:
			half_button=True
		width-=2*self.margin_x
		
		if half_button: # we want half button
			if x==0:
				xi=x+self.margin_x
				xf=xi+0.5-self.margin_x*1.5
			else:
				xf=x-self.margin_x
				xi=xf-0.5+self.margin_x*1.5
		else:
			xi=x+self.margin_x
			xf=xi+width

		cr.set_line_width(linea)
	
		cor=float(bgcolor[0])/65535.0
		cog=float(bgcolor[1])/65535.0
		cob=float(bgcolor[2])/65535.0
		coa=float(bgcolor[3])/65535.0
		cr.set_source_rgba(cor,cog,cob,coa)

		cr.move_to(xi,y-border)
		cr.line_to(xf,y-border)
		cr.curve_to(xf+radius,y-border,xf+radius,y+height+border,xf,y+height+border)
		cr.line_to(xi,y+height+border)
		cr.curve_to(xi-radius,y+height+border,xi-radius,y-border,xi,y-border)
		cr.fill()

		arrowx=(xi+xf)/2
		if x==0:
			arrowx+=0.0175
			s=True
		else:
			s=False
			arrowx-=0.0175
			
			
		self.menu_paint_arrow(cr, arrowx+self.shadow_offset, y+self.shadow_offset, s, height, shcolor)
		self.menu_paint_arrow(cr, arrowx, y, s, height, fgcolor)

	
	def menu_paint_arrow(self,cr,x,y,s,height,color):
	
		if color==None:
			return
	
		cor=float(color[0])/65535.0
		cog=float(color[1])/65535.0
		cob=float(color[2])/65535.0
		coa=float(color[3])/65535.0
		cr.set_source_rgba(cor,cog,cob,coa)

		cr.move_to(x,y)
		if s:
			cr.line_to(x-0.035,y+height/2)
		else:
			cr.line_to(x+0.035,y+height/2)
		cr.line_to(x,y+height)
		cr.line_to(x,y)
		cr.fill()

		
	def menu_set_text(self,cr,x,y,halign,texto,bgcolor,fontcolor,myfontname="Sans",myfontstyle=cairo.FONT_WEIGHT_BOLD,myfontslant=cairo.FONT_SLANT_NORMAL,myfontsize=12,vcenter=True):

		fontsize2=myfontsize*0.00315

		cr.select_font_face(myfontname,myfontslant,myfontstyle)

		# I created the button image for this size, so I must respect it :(
		#xb,yb,width,height,cx,cy=cr.text_extents("Título 1")
		height=0.0391604010025
	
		cr.set_font_size(fontsize2)
		xb,y2,width,h2,cx,cy2=cr.text_extents(texto)

		#if ((bgcolor[0]<512) and (bgcolor[1]<512) and (bgcolor[2]<512)):
		#	bgcolor[0]=512
		#	bgcolor[1]=512
		#	bgcolor[2]=512
			
		#if ((fontcolor[0]<512) and (fontcolor[1]<512) and (fontcolor[2]<512)):
		#	fontcolor[0]=512
		#	fontcolor[1]=512
		#	fontcolor[2]=512
		
		cor=float(fontcolor[0])/65535.0
		cog=float(fontcolor[1])/65535.0
		cob=float(fontcolor[2])/65535.0
		coa=float(fontcolor[3])/65535.0
		cr.set_source_rgba(cor,cog,cob,coa)
		if halign==2: # center
			nx=.5-width/2.0-xb
		elif halign==0: # left
			nx=self.margin_x
		elif halign==1: # right
			nx=1.0-self.margin_x-width
		
		nx+=x
		
		if vcenter:
			ny=y-y2+(height-h2)/2.0
		else:
			ny=y-y2+(height-h2)

		cr.move_to(nx,ny)		
		cr.show_text(texto)


	def create_menu_bg(self,counter,element,paint_bg=0):

		""" Paints the menu in a Cairo surface.	PAINT_BG can be:
			0: paints everything for the base picture
			1: paints the HIGHLIGHT picture
			2: paints the ACTIVE picture
			3: paints the SELECT picture		
		"""

		if paint_bg==0:
			try:
				print "Uso "+str(self.menu_bg)
				extra_pixbuf = gtk.gdk.pixbuf_new_from_file(self.menu_bg)
				extra_x = extra_pixbuf.get_width()
				extra_y = extra_pixbuf.get_height()

				sf_base = cairo.ImageSurface(0,extra_x,extra_y)

				extra_ct = cairo.Context(sf_base)
				extra_ct2 = gtk.gdk.CairoContext(extra_ct)

				extra_ct2.set_source_pixbuf(extra_pixbuf,0,0)
				extra_ct2.paint()
				extra_ct2.stroke()
			except:
				return None

		if self.menu_PAL:
			y=576.0
		else:
			y=480.0

		sf=cairo.ImageSurface(cairo.FORMAT_ARGB32,720,int(y))
		cr=cairo.Context(sf)
		if paint_bg!=0: # if we are creating something different than the base, we use a 1bit surface
			fo=cairo.FontOptions()
			fo.set_antialias(cairo.ANTIALIAS_NONE)
			cr.set_font_options(fo)
			cr.set_antialias(cairo.ANTIALIAS_NONE)
		else:
			cr.set_source_rgb(1.0,1.0,1.0)
			cr.paint()

		cr.identity_matrix()
		
		if paint_bg==0:
			wbase=float(sf_base.get_width())
			hbase=float(sf_base.get_height())
			cr.scale(720.0/wbase,y/hbase)
			cr.set_source_surface(sf_base)
			cr.paint()
			cr.identity_matrix()
		

		cr.scale(sf.get_width(),1.33*sf.get_height()) # picture gets from 0 to 1 in X and from 0 to 0.75 in Y

		pos_y=0.125
		
		if self.align!=0:
			pos_y+=0.05*float((self.lines_per_menu-len(self.structure[counter:counter+self.elements_per_menu]))/self.align)

		fontname,fontstyle,fontslant,fontsize=devede_other.get_font_params(self.font_name)

		shadowcolor=self.shadowcolor
		if paint_bg!=2:
			pos_y2=pos_y
			if paint_bg==0:
				bgcolor=self.bgcolor
				fontcolor=self.fontcolor
				arrowcolor=self.fontcolor
				arrowshadowcolor=shadowcolor
			elif paint_bg==1:
				bgcolor=[0,0,0,0]
				fontcolor=self.activecolor
				arrowcolor=self.activecolor
				strokecolor=self.activecolor
				arrowshadowcolor=None
			elif paint_bg==2:
				bgcolor=[0,0,0,0]
				fontcolor=self.activecolor
				arrowcolor=self.activecolor
				strokecolor=self.activecolor
				arrowshadowcolor=None
			else:
				bgcolor=[0,0,0,0]
				fontcolor=self.inactivecolor
				arrowcolor=self.inactivecolor
				strokecolor=self.inactivecolor
				arrowshadowcolor=None
				
			for entrada in self.structure[counter:counter+self.elements_per_menu]:
				print pos_y
				self.menu_set_bg(cr, 0, pos_y, 1, bgcolor)
				if paint_bg==0: # print the shadow first
					self.menu_set_text(cr,self.shadow_offset,pos_y+self.shadow_offset,self.halign,entrada[0]["nombre"],bgcolor,shadowcolor,fontname,fontstyle,fontslant,fontsize)
				self.menu_set_text(cr,0,pos_y,self.halign,entrada[0]["nombre"],bgcolor,fontcolor,fontname,fontstyle,fontslant,fontsize)
				pos_y+=0.05

			print "Paint_bg "+str(paint_bg)+" title text: "+str(self.title_text)
			if (paint_bg==0) and (self.title_text!=""):
				print "pongo titulo "+self.title_text
				fontname,fontstyle,fontslant,fontsize=devede_other.get_font_params(self.title_fontname)
				self.menu_set_text(cr,self.shadow_offset, 0.075+self.shadow_offset,2,self.title_text, [0,0,0,0], self.title_shadow, fontname, fontstyle, fontslant, fontsize, False)
				self.menu_set_text(cr,0, 0.075,2,self.title_text, [0,0,0,0], self.title_color, fontname, fontstyle, fontslant, fontsize, False)

			pos_y=0.625
			# check if we have to paint the NEXT MENU button
			if (element!=self.nmenues-1) and (self.nmenues>1):
				self.menu_set_bg(cr, 1, pos_y, 0.4, bgcolor,arrowcolor,arrowshadowcolor)
			# check if we have to paint the PREVIOUS MENU button
			if (element!=0) or ((self.extcr!=None) and (self.nmenues>1)):
				self.menu_set_bg(cr, 0, pos_y, 0.4, bgcolor,arrowcolor,arrowshadowcolor)

		if self.extcr==None:
			if paint_bg==0:
				sf.write_to_png(self.filefolder+self.filename+"_menu"+str(element)+"_bg.png")
			elif paint_bg==1:
				sf.write_to_png(self.filefolder+self.filename+"_menu"+str(element)+"_bg_active_out.png")
			elif paint_bg==2:
				sf.write_to_png(self.filefolder+self.filename+"_menu"+str(element)+"_bg_inactive_out.png")
			else:
				sf.write_to_png(self.filefolder+self.filename+"_menu"+str(element)+"_bg_select_out.png")
		return sf

	
	def create_menu_mpg(self,counter):
	
		print "Creating menus"
		
		self.mplexed=False
		command_var=[]
		if (sys.platform=="win32") or (sys.platform=="win64"):
			command_var=["mencoder.exe"]
		else:
			command_var=["mencoder"]
	
		currentfile=self.filefolder+self.filename+"_menu_"+str(counter)+".mpg"
	
		command_var.append("-srate")
		command_var.append("48000")
		command_var.append("-af")
		command_var.append("lavcresample=48000")
		command_var.append("-oac")
		command_var.append("lavc")
		command_var.append("-ovc")
		command_var.append("lavc")
		command_var.append("-of")
		command_var.append("mpeg")
		command_var.append("-mpegopts")
		command_var.append("format=dvd:tsaf")
		command_var.append("-ofps")
		audio=self.menu_sound
		#audio="/home/raster/Escritorio/lazy.mp3"
		if self.menu_PAL:
			command_var.append("25")
		else:
			command_var.append("30000/1001")

		wide="4/3"
		command_var.append("-vf")
		if self.menu_PAL:
			command_var.append("scale=720:576,harddup")
		else:
			command_var.append("scale=720:480,harddup")
		command_var.append("-lavcopts")
		if self.threads>8:
			nthreads=8
		else:
			nthreads=self.threads
		
		if nthreads>1:
			lavcopts="threads="+str(nthreads)+":"
		else:
			lavcopts=""
		lavcopts+="vcodec=mpeg2video:sc_threshold=1000000000:cgop:trell:mbd=2:vstrict=0:"
		lavcopts+="vrc_maxrate=7000:vrc_buf_size=1835:vbitrate=1000:keyint=12:"
		lavcopts+="acodec=ac3:abitrate=128:aspect="+wide
		command_var.append(lavcopts)
		command_var.append("-o")
		command_var.append(currentfile)
		command_var.append("-audiofile")
		command_var.append(audio)
		command_var.append("-mf")
		command_var.append("type=png:fps=1/"+str(self.menu_sound_duration))
		origDir=os.getcwd()
		if (sys.platform=="win32") or (sys.platform=="win64"):
			temp=os.path.split(self.filefolder+self.filename+"_menu"+str(counter)+"_bg.png")
			picDir=temp[0]
			picName=temp[1]
			command_var.append("mf://"+picName)
			os.chdir(picDir)
		else:
			command_var.append("mf://"+self.filefolder+self.filename+"_menu"+str(counter)+"_bg.png")
		print "Lanzo "+str(command_var)

		self.launch_program(command_var)
		
		if (sys.platform=="win32") or (sys.platform=="win64"):
			os.chdir(origDir)

	
	def menu_mplex_buttons(self,counter):
	
		self.mplexed=True
		if (sys.platform=="win32") or (sys.platform=="win64"):
			comando=["spumux.exe"]
			# The -i -o is with a custom patched version of
			# dvdauthor.  Best and easiest way of making it work
			comando.append(self.filefolder+self.filename+"_menu_"+str(counter)+".xml")
			comando.append("-i")
			comando.append(self.filefolder+self.filename+"_menu_"+str(counter)+".mpg")
			comando.append("-o")
			comando.append(self.filefolder+self.filename+"_menu2_"+str(counter)+".mpg")
			self.launch_program(comando)
		else:
			comando="spumux"
			
			comando+=' "' +self.filefolder+self.filename+'_menu_'+str(counter)+'.xml"'

			print "Launch: "+comando
			self.launch_shell(comando,stdinout=[self.filefolder+self.filename+"_menu_"+str(counter)+".mpg",self.filefolder+self.filename+"_menu2_"+str(counter)+".mpg"])


	def end_process(self,eraser,erase_temporary_files):
		
		if erase_temporary_files and self.mplexed:
			eraser.delete_menu_temp()
