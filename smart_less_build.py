import sublime, sublime_plugin

try:
  import executer
except ImportError:
  from . import executer

import os.path

# from inspect import getmembers
# from pprint import pprint



def cwd_for_window(window):
	"""
	Return the working directory in which the window's commands should run.

	In the common case when the user has one folder open, return that.
	Otherwise, return one of the following (in order of preference):
		1) One of the open folders, preferring a folder containing the active
		   file.
		2) The directory containing the active file.
		3) The user's home directory.
	"""
	folders = window.folders()
	if len(folders) == 1:
		return folders[0]
	else:
		active_view = window.active_view()
		active_file_name = active_view.file_name() if active_view else None
		if not active_file_name:
			return folders[0] if len(folders) else os.path.expanduser("~")
		for folder in folders:
			if active_file_name.startswith(folder):
				return folder
		return os.path.dirname(active_file_name)


# def dump(obj):
#	pprint( getmembers( obj ) )


# class name not important
class smartLessBuild(sublime_plugin.EventListener):
	def relaodSettings(self):
		self.global_settings = sublime.load_settings('smart_less_build.sublime-settings')
		self.project_settings = sublime.active_window().project_data().get('smart_less_build')
		if self.project_settings == None:
			self.project_settings = {}
	def get(self,key):
		return self.project_settings.get(key,self.global_settings.get(key))
	def on_post_save(self, view):
		if not "source.less" in view.scope_name(0):
			return
		self.relaodSettings()
		window = sublime.active_window()

		cmd = ""

		if self.get('working_dir').lower() == '@auto':
			working_dir = cwd_for_window(sublime.active_window())
		elif self.get('working_dir').lower() == '@less_dir':
			working_dir = os.path.dirname(view.file_name())
		elif os.path.exists(self.get('working_dir')):
			working_dir = self.get('working_dir')
		elif self.get('skip_config_err'):
			working_dir = cwd_for_window(sublime.active_window())
		else:
			sublime.error_message("working_dir not found")
			return

		if self.get('main_less') == "@none":
			main_less = view.file_name()
		elif os.path.exists(self.get('main_less')) or os.path.exists( working_dir + "/" + self.get('main_less')):
			main_less = self.get('main_less')
		elif self.get('skip_config_err'):
			main_less = view.file_name()
		else:
			sublime.error_message("main_less not found")
			return

		if self.get('css_dir') == "@same_dir":
			css_dir = "\\".join( main_less.split('\\')[:-1])
		elif os.path.exists(self.get('css_dir')):
			css_dir = self.get('css_dir')
		elif os.path.exists( working_dir + "/" + self.get('css_dir') ):
			css_dir = working_dir + "/" + self.get('css_dir')
		elif self.get('skip_config_err'):
			css_dir = "\\".join( main_less.split('\\')[:-1])
		else:
			sublime.error_message("css_dir not found")
			return
		
		if os.path.isdir( css_dir ):
			css_dir += "/" + os.path.splitext( os.path.basename( main_less ) )[0] + ".css"

		if self.get('source_map'):
			cmd +=" --source-map"
		if self.get('minify'):
			cmd +=" --compress"

		cmd +=" --no-color"
		window.run_command("executer", {
			'cmd': 'lessc "'+ main_less +'" "'+ css_dir+'" '+cmd+' '+self.get('custom_args'),
			'shell': True,
			'working_dir': working_dir,
			# 'syntax': 'Packages/LESS/LESS.tmLanguage',
			'encoding': "utf_8"
		})


