import "./globals.css";
import AppShell from "./components/AppShell";

export const metadata = {
  title: "CoffeeStudio",
  description: "CoffeeStudio Platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="de">
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
