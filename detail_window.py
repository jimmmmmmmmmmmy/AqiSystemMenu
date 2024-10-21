import objc
from Foundation import NSObject, NSMakeRect, NSUserDefaults
from AppKit import (
    NSWindow, NSWindowStyleMaskTitled, NSWindowStyleMaskClosable,
    NSBackingStoreBuffered, NSScreen, NSApp, NSFloatingWindowLevel,
    NSColor, NSButton, NSButtonTypeSwitch, NSBezelStyleRounded,
    NSControlStateValueOn, NSControlStateValueOff
)
from aqi_visualization_view import AQIVisualizationView

class DetailWindow(NSObject):
    window = objc.ivar()
    checkbox = objc.ivar()
    done_button = objc.ivar()
    
    def init(self):
        self = objc.super(DetailWindow, self).init()
        if self:
            self.window = None
            self.checkbox = None
            self.done_button = None
        return self

    @objc.python_method
    def showWindow_withText_andData_(self, title, text, data):
        windowWidth = 550
        windowHeight = 550
        padding = 35

        if self.window is None:
            screen = NSScreen.mainScreen()
            screenRect = screen.frame()
            
            windowRect = NSMakeRect((screenRect.size.width - windowWidth) / 2,
                                    (screenRect.size.height - windowHeight) / 2,
                                    windowWidth, windowHeight)
            
            styleMask = NSWindowStyleMaskTitled | NSWindowStyleMaskClosable
            
            self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                windowRect, styleMask, NSBackingStoreBuffered, False)
            
            self.window.setLevel_(NSFloatingWindowLevel)
        
        # Always set the window size
        self.window.setFrame_display_(NSMakeRect(self.window.frame().origin.x,
                                                 self.window.frame().origin.y,
                                                 windowWidth, windowHeight), True)
        self.window.setMinSize_((windowWidth, windowHeight))
        self.window.setMaxSize_((windowWidth, windowHeight))

        self.window.setTitle_(title)
        self.window.setReleasedWhenClosed_(False)
        self.window.setDelegate_(self)

        # Set the background color to match the default gray color
        self.window.setBackgroundColor_(NSColor.windowBackgroundColor())

        contentView = self.window.contentView()
        for subview in contentView.subviews():
            subview.removeFromSuperview()

        # Create visualization view with padding
        visualizationView = AQIVisualizationView.alloc().initWithFrame_andData_(
            NSMakeRect(padding, padding + 40, windowWidth - 2*padding, windowHeight - 2*padding - 40), data
        )
        contentView.addSubview_(visualizationView)

        # Add checkbox
        self.checkbox = NSButton.alloc().initWithFrame_(NSMakeRect(padding, 10, 200, 20))
        self.checkbox.setButtonType_(NSButtonTypeSwitch)
        self.checkbox.setTitle_("Start OpenAir at login")
        self.checkbox.setState_(NSControlStateValueOn if self.isLoginItemEnabled() else NSControlStateValueOff)
        self.checkbox.setTarget_(self)
        self.checkbox.setAction_(objc.selector(self.toggleLoginItem_, signature=b'v@:'))
        contentView.addSubview_(self.checkbox)

        # Add Done button
        self.done_button = NSButton.alloc().initWithFrame_(NSMakeRect(windowWidth - padding - 80, 10, 80, 30))
        self.done_button.setTitle_("Done")
        self.done_button.setBezelStyle_(NSBezelStyleRounded)
        self.done_button.setTarget_(self)
        self.done_button.setAction_(objc.selector(self.closeWindow_, signature=b'v@:'))
        contentView.addSubview_(self.done_button)

        self.window.makeKeyAndOrderFront_(None)
        NSApp.activateIgnoringOtherApps_(True)

    @objc.python_method
    def isLoginItemEnabled(self):
        # Implement logic to check if the app is set to start at login
        # This is a placeholder and should be replaced with actual implementation
        return NSUserDefaults.standardUserDefaults().boolForKey_("StartAtLogin")

    @objc.python_method
    def toggleLoginItem_(self, sender):
        # Implement logic to toggle start at login setting
        # This is a placeholder and should be replaced with actual implementation
        isEnabled = sender.state() == NSControlStateValueOn
        NSUserDefaults.standardUserDefaults().setBool_forKey_(isEnabled, "StartAtLogin")
        NSUserDefaults.standardUserDefaults().synchronize()

    @objc.python_method
    def closeWindow_(self, sender):
        if self.window:
            NSApp.performSelectorOnMainThread_withObject_waitUntilDone_(
                objc.selector(self._closeWindowOnMainThread, signature=b'v@:'),
                None,
                True
            )

    @objc.python_method
    def _closeWindowOnMainThread(self):
        NSApp.stopModal()
        self.window.orderOut_(None)
        self.window.close()
        self.window = None

    def windowWillClose_(self, notification):
        NSApp.stopModal()
        self.window = None

    def windowShouldClose_(self, sender):
        return True

    def dealloc(self):
        if self.window:
            self.window.setDelegate_(None)
            self.window.close()
        self.window = None
        objc.super(DetailWindow, self).dealloc()