import Nav from "./components/Nav";

export const metadata = { title: "CoffeeStudio", description: "CoffeeStudio Platform" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="de">
      <body style={{ fontFamily: "system-ui, sans-serif", margin: 0, padding: 0 }}>
        <div style={{ padding: 16, borderBottom: "1px solid #eee" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
            <b>CoffeeStudio</b> — Option D v0.2.0
            <Nav />
          </div>
        </div>
        <div style={{ padding: 16 }}>{children}</div>
      </body>
    </html>
  );
}
