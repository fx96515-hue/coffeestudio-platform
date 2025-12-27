import Link from "next/link";

export default function Home() {
  return (
    <div>
      <h1>Start</h1>
      <ul>
        <li><Link href="/login">Login</Link></li>
        <li><Link href="/dashboard">Dashboard</Link></li>
        <li><Link href="/cooperatives">Kooperativen</Link></li>
        <li><Link href="/roasters">Röster</Link></li>
        <li><Link href="/lots">Lots</Link></li>
        <li><Link href="/reports">Reports</Link></li>
      </ul>
    </div>
  );
}
