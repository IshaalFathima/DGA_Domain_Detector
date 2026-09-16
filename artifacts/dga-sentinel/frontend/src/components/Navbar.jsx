import { NavLink } from 'react-router-dom'
import './Navbar.css'

export default function Navbar() {
  return (
    <nav className="navbar" aria-label="Main navigation">
      <div className="navbar-inner container">
        <NavLink to="/" className="navbar-brand" aria-label="DGA Sentinel home">
          <span className="brand-shield">◈</span>
          <span className="brand-name">DGA<span className="brand-sep"> </span>SENTINEL</span>
        </NavLink>

        <div className="navbar-links">
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              `nav-link${isActive ? ' nav-link--active' : ''}`
            }
          >
            Analyze
          </NavLink>
          <NavLink
            to="/about"
            className={({ isActive }) =>
              `nav-link${isActive ? ' nav-link--active' : ''}`
            }
          >
            About
          </NavLink>
        </div>
      </div>
    </nav>
  )
}
