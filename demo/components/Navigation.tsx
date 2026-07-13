import Link from 'next/link'
import styles from './Navigation.module.css'

export default function Navigation() {
  return (
    <nav className={styles.nav}>
      <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Link href="/" className={styles.logo}>
          T1_AD
        </Link>
        <ul className={styles.menu}>
          <li>
            <Link href="/">Dashboard</Link>
          </li>
          <li>
            <Link href="/transformation">Transformation</Link>
          </li>
          <li>
            <Link href="/analysis">Analysis</Link>
          </li>
          <li>
            <Link href="/comparison">Comparison</Link>
          </li>
          <li>
            <Link href="/details">Details</Link>
          </li>
        </ul>
      </div>
    </nav>
  )
}
