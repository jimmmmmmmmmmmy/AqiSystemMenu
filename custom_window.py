import objc
from Foundation import NSObject, NSMakeRect
from AppKit import (
    NSWindow, NSWindowStyleMaskTitled, NSWindowStyleMaskClosable, NSWindowStyleMaskMiniaturizable,
    NSWindowStyleMaskResizable, NSBackingStoreBuffered, NSScreen, NSTextField, NSFont,
    NSApplication, NSToolbar, NSToolbarItem, NSImage, NSMenuItem, NSMenu,
    NSToolbarFlexibleSpaceItemIdentifier, NSToolbarSpaceItemIdentifier,
    NSStatusWindowLevel, NSTextAlignmentCenter, NSToolbarDisplayModeIconAndLabel
)

class CustomWindow(NSObject):
    def init(self):
        self = objc.super(CustomWindow, self).init()
        if self is None:
            return None
        self.app = None
        self.window = None
        return self

    def showWindow_withText_andApp_(self, title, text, app):
        self.app = app
        if self.window is None or not self.window.isVisible():
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

            self.window.setTitle_(title)

            # Create the text field
            textField = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 20, windowWidth - 40, windowHeight - 80))
            textField.setEditable_(False)
            textField.setBezeled_(False)
            textField.setDrawsBackground_(False)
            textField.setFont_(NSFont.fontWithName_size_("Helvetica", 12))
            self.window.contentView().addSubview_(textField)

            # Set the window delegate to self
            self.window.setDelegate_(self)

        textField = self.window.contentView().subviews()[0]
        textField.setStringValue_(text)

        self.window.makeKeyAndOrderFront_(None)
        NSApplication.sharedApplication().activateIgnoringOtherApps_(True)

    def windowShouldClose_(self, sender):
        self.closeWindow()
        if self.app is not None:
            self.app.custom_window = None
        return True

    def closeWindow(self):
        if self.window:
            self.window.orderOut_(None)
            self.window = None

    def toolbar_itemForItemIdentifier_willBeInsertedIntoToolbar_(self, toolbar, itemIdentifier, flag):
        item = NSToolbarItem.alloc().initWithItemIdentifier_(itemIdentifier)
        if itemIdentifier == "AppTitle":
            item.setLabel_("AQI App Preferences")
            item.setPaletteLabel_("App Title")
            titleField = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 0, 200, 32))
            titleField.setStringValue_("AQI App Preferences")
            titleField.setEditable_(False)
            titleField.setBezeled_(False)
            titleField.setDrawsBackground_(False)
            titleField.setAlignment_(NSTextAlignmentCenter)
            titleField.setFont_(NSFont.boldSystemFontOfSize_(14))
            item.setView_(titleField)
        elif itemIdentifier == "Preferences":
            item.setLabel_("Preferences")
            item.setPaletteLabel_("Preferences")
            item.setImage_(NSImage.imageNamed_("NSPreferencesGeneral"))
            item.setTarget_(self)
            item.setAction_("showPreferences:")
        return item

    def toolbarAllowedItemIdentifiers_(self, toolbar):
        return ["AppTitle", "Preferences", NSToolbarFlexibleSpaceItemIdentifier, NSToolbarSpaceItemIdentifier]

    def toolbarDefaultItemIdentifiers_(self, toolbar):
        return [NSToolbarFlexibleSpaceItemIdentifier, "AppTitle", NSToolbarFlexibleSpaceItemIdentifier, "Preferences"]

    def showPreferences_(self, sender):
        # Implement preferences window logic here
        print("Show Preferences")

    # Additional required methods for NSToolbarDelegate
    def toolbarWillAddItem_(self, notification):
        pass

    def toolbarDidRemoveItem_(self, notification):
        pass

    def toolbarSelectableItemIdentifiers_(self, toolbar):
        return []