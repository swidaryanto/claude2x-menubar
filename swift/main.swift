import AppKit
import Foundation

// MARK: - Timezones & Constants

private let ptZone     = TimeZone(identifier: "America/Los_Angeles")!
private let wibZone    = TimeZone(identifier: "Asia/Jakarta")!
private let plistLabel = "com.claude2x.app"
private let frameCount = 24
private let animInterval: TimeInterval = 0.05

private let expiryDate: Date = {
    var cal = Calendar(identifier: .gregorian)
    cal.timeZone = wibZone
    var c = DateComponents()
    c.year = 2026; c.month = 3; c.day = 29
    c.hour = 23;   c.minute = 59; c.second = 59
    return cal.date(from: c)!
}()

// MARK: - Status Logic

func getStatus() -> (is2x: Bool, now: Date) {
    let now = Date()
    var cal = Calendar(identifier: .gregorian)
    cal.timeZone = ptZone
    let weekday = cal.component(.weekday, from: now) // 1=Sun … 7=Sat
    let hour    = cal.component(.hour,    from: now)
    if weekday == 1 || weekday == 7 { return (true, now) }
    return (!(hour >= 5 && hour < 11), now)
}

func formatWIB(_ date: Date) -> String {
    let fmt = DateFormatter()
    fmt.timeZone  = wibZone
    fmt.dateFormat = "h:mm a 'WIB'"
    return fmt.string(from: date)
}

func minsStr(_ secs: TimeInterval) -> String {
    let total = Int(abs(secs) / 60)
    let h = total / 60, m = total % 60
    return h > 0 ? "\(h)h \(m)m" : "\(m)m"
}

func nextDate(hour targetHour: Int, addDays: Int = 0, from now: Date) -> Date {
    var cal = Calendar(identifier: .gregorian)
    cal.timeZone = ptZone
    let base = addDays > 0 ? cal.date(byAdding: .day, value: addDays, to: now)! : now
    return cal.date(bySettingHour: targetHour, minute: 0, second: 0, of: base)!
}

struct MenuContent { let title, line1, line2: String }

func buildMenuContent(is2x: Bool, now: Date) -> MenuContent {
    var cal = Calendar(identifier: .gregorian)
    cal.timeZone = ptZone
    let weekday   = cal.component(.weekday, from: now)
    let hour      = cal.component(.hour,    from: now)
    let isWeekend = weekday == 1 || weekday == 7

    if is2x {
        if isWeekend {
            return MenuContent(
                title: "2x",
                line1: "●  Double limits active",
                line2: "All weekend — no reset until Monday"
            )
        }
        let peak = hour < 5
            ? nextDate(hour: 5, from: now)
            : nextDate(hour: 5, addDays: 1, from: now)
        return MenuContent(
            title: "2x",
            line1: "●  Double limits active",
            line2: "↻  Resets in \(minsStr(peak.timeIntervalSince(now))) — at \(formatWIB(peak))"
        )
    } else {
        let resume = nextDate(hour: 11, from: now)
        return MenuContent(
            title: "1x",
            line1: "○  Normal limits right now",
            line2: "↻  Double limits in \(minsStr(resume.timeIntervalSince(now))) — at \(formatWIB(resume))"
        )
    }
}

func buildExpiresLine(now: Date) -> String {
    let diff = expiryDate.timeIntervalSince(now)
    let days = Int(diff / 86400)
    if diff <= 0  { return "◆  This benefit has ended (Mar 29)" }
    if days == 0  { return "◆  Ends today — make the most of it" }
    if days == 1  { return "◆  Ends tomorrow, Mar 29" }
    if days <= 5  { return "◆  Ends Mar 29  ·  \(days) days left" }
    return          "◆  Ends Mar 29, 2026  ·  \(days) days left"
}

// MARK: - Login Item

func plistPath() -> String {
    let home = FileManager.default.homeDirectoryForCurrentUser.path
    return "\(home)/Library/LaunchAgents/\(plistLabel).plist"
}
func isLoginEnabled() -> Bool { FileManager.default.fileExists(atPath: plistPath()) }

func enableLogin() {
    let plist: [String: Any] = [
        "Label": plistLabel,
        "ProgramArguments": ["/usr/bin/open", "-a", Bundle.main.bundlePath],
        "RunAtLoad": true, "KeepAlive": false
    ]
    let dir = (plistPath() as NSString).deletingLastPathComponent
    try? FileManager.default.createDirectory(atPath: dir, withIntermediateDirectories: true)
    let data = try! PropertyListSerialization.data(fromPropertyList: plist, format: .xml, options: 0)
    try? data.write(to: URL(fileURLWithPath: plistPath()))
}
func disableLogin() { try? FileManager.default.removeItem(atPath: plistPath()) }

// MARK: - App Delegate

class AppDelegate: NSObject, NSApplicationDelegate {
    var statusItem: NSStatusItem!
    var frames:     [NSImage] = []
    var frameIndex  = 0

    var line1Item   = NSMenuItem()
    var line2Item   = NSMenuItem()
    var expiresItem = NSMenuItem()
    var loginItem   = NSMenuItem()

    func applicationDidFinishLaunching(_ note: Notification) {
        NSApp.setActivationPolicy(.accessory) // hide Dock icon
        loadFrames()
        setupStatusItem()
        setupMenu()
        updateStatus()
        Timer.scheduledTimer(withTimeInterval: animInterval, repeats: true) { [weak self] _ in self?.tick() }
        Timer.scheduledTimer(withTimeInterval: 30,           repeats: true) { [weak self] _ in self?.updateStatus() }
    }

    func loadFrames() {
        let dir = (Bundle.main.resourcePath ?? "") + "/frames"
        for i in 0..<frameCount {
            let path = String(format: "\(dir)/frame_%03d.png", i)
            if let img = NSImage(contentsOfFile: path) {
                img.isTemplate = true
                frames.append(img)
            }
        }
    }

    func setupStatusItem() {
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        if let btn = statusItem.button {
            btn.image         = frames.first
            btn.title         = " 1x"
            btn.imagePosition = .imageLeft
        }
    }

    func infoItem(_ title: String) -> NSMenuItem {
        let item = NSMenuItem(title: title, action: #selector(noop), keyEquivalent: "")
        item.target = self
        return item
    }

    func setupMenu() {
        let menu = NSMenu()
        menu.appearance = NSAppearance(named: .darkAqua)

        line1Item   = infoItem("")
        line2Item   = infoItem("")
        expiresItem = infoItem("")

        [line1Item, line2Item].forEach { menu.addItem($0) }
        menu.addItem(.separator())
        menu.addItem(infoItem("When you get double limits:"))
        menu.addItem(infoItem("  • Weeknights  7pm – 1am WIB"))
        menu.addItem(infoItem("  • All weekend, all day"))
        menu.addItem(.separator())
        menu.addItem(expiresItem)
        menu.addItem(.separator())

        loginItem = NSMenuItem(title: "Start at Login", action: #selector(toggleLogin), keyEquivalent: "")
        loginItem.target = self
        loginItem.state  = isLoginEnabled() ? .on : .off
        menu.addItem(loginItem)
        menu.addItem(.separator())
        menu.addItem(NSMenuItem(title: "Quit", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q"))

        statusItem.menu = menu
    }

    @objc func tick() {
        frameIndex = (frameIndex + 1) % max(frames.count, 1)
        statusItem.button?.image = frames[frameIndex]
    }

    @objc func updateStatus() {
        let (is2x, now) = getStatus()
        let c = buildMenuContent(is2x: is2x, now: now)
        DispatchQueue.main.async { [weak self] in
            guard let self else { return }
            self.statusItem.button?.title = " \(c.title)"
            self.line1Item.title          = c.line1
            self.line2Item.title          = c.line2
            self.expiresItem.title        = buildExpiresLine(now: now)
        }
    }

    @objc func toggleLogin() {
        if isLoginEnabled() { disableLogin(); loginItem.state = .off }
        else                 { enableLogin();  loginItem.state = .on  }
    }

    @objc func noop() {}
}

// MARK: - Entry Point
let app      = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.run()
