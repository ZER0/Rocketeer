import sublime, sublime_plugin
import os, re

class AddonSDKCompletition(sublime_plugin.EventListener):
  search = re.compile(r"\brequire\s*\(\s*[\"\'](.*)").search;
  settings = sublime.load_settings("Rocketeer.sublime-settings")

  def on_query_completions(self, view, prefix, locations):
    #current_file = view.file_name()

    path = os.path.dirname(view.file_name())

    caret = view.sel()[0].begin()

    scope = view.scope_name(caret).strip().split(" ")
    is_js_string = ("string.quoted.double.js" in scope) or ("string.quoted.single.js" in scope)

    sdk_path = self.settings.get("path")

    results = []

    line = view.line(caret)
    region = sublime.Region(line.begin(), caret);

    module_path = self.search(view.substr(region))

    is_require = is_js_string and module_path

    if not sdk_path or (not(os.path.exists(sdk_path) and is_require)):
      return results

    module_name = module_path.group(1)

    pos = module_name.rfind("/")

    is_relative = module_name[0] == "."

    if pos > -1 and is_relative:
      path = os.path.realpath(os.path.join(path, module_name[0:pos]))
      module_name = module_name[pos:]
    else:
      path = sdk_path

    cmd = "find '" + path + "' -regex '.*" + re.escape(module_name) + ".*\.js$'"

    f = os.popen(cmd)
    for i in f.readlines():
      item = i.strip()[len(path) + 1:-3]
      results.append([i.strip()[len(path) + 1:-3]])

    items = []

    # ugly code to handle some weird condition
    for sublist in results:
      for item in sublist:
        if pos > - 1 and not is_relative and item.count("/") > 1:
          items.append((item, item[pos + 1:]))
        else:
          items.append((item, item))

    #results = [(item, item) for sublist in results for item in sublist] #flatten

    results = list(set(items)) # make unique
    results.sort() # sort

    return results
