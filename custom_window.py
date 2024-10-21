import objc
from Foundation import NSObject, NSMakeRect
from AppKit import (
    NSWindow, NSWindowStyleMaskTitled, NSWindowStyleMaskClosable, NSWindowStyleMaskMiniaturizable,
    NSWindowStyleMaskResizable, NSBackingStoreBuffered, NSScreen, NSTextField, NSFont,
    NSApplication, NSStatusWindowLevel, NSTextAlignmentCenter
)

class CustomWindow(NSObject):
    window = objc.ivar()
    
    def init(self):
        self = objc.super(CustomWindow, self).init()
        if self is None:
            return None
        self.window = None
        return self

    def showWindow_withText_(self, title, text):
        if self.window is None:
            screen = NSScreen.mainScreen()
            screenRect = screen.frame()
            windowWidth = 400
            windowHeight = 300
            windowRect = NSMakeRect((screenRect.size.width - windowWidth) / 2,
                                    (screenRect.size.height - windowHeight) / 2,
                                    windowWidth, windowHeight)
            styleMask = (NSWindowStyleMaskTitled | NSWindowStyleMaskClosable |
                         NSWindowStyleMaskMiniaturizable | NSWindowStyleMaskResizable)
            self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                windowRect, styleMask, NSBackingStoreBuffered, False)
            self.window.setReleasedWhenClosed_(False)
            self.window.setDelegate_(self)

        self.window.setTitle_(title)

        contentView = self.window.contentView()
        for subview in contentView.subviews():
            subview.removeFromSuperview()

        textField = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 20, 360, 260))
        textField.setEditable_(False)
        textField.setBezeled_(False)
        textField.setDrawsBackground_(False)
        textField.setFont_(NSFont.fontWithName_size_("Helvetica", 12))
        textField.setStringValue_(text)
        contentView.addSubview_(textField)

        self.window.makeKeyAndOrderFront_(None)
        NSApplication.sharedApplication().activateIgnoringOtherApps_(True)

    def windowWillClose_(self, notification):
        self.window.setDelegate_(None)
        self.window = None

    def windowShouldClose_(self, sender):
        return True

    def dealloc(self):
        if self.window:
            self.window.setDelegate_(None)
            self.window.close()
        self.window = None
        objc.super(CustomWindow, self).dealloc()