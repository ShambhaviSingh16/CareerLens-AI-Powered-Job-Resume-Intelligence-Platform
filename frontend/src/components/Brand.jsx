import { Link } from "react-router-dom";

export function Icon({ name = "arrow", size = 20, ...props }) {
  const paths = {
    arrow: <><path d="M5 12h14M13 6l6 6-6 6" /></>,
    upload: <><path d="M12 16V4m-5 5 5-5 5 5M4 16v4h16v-4" /></>,
    file: <><path d="M14 3H5v18h14V8zM14 3v6h5M8 13h8M8 17h5" /></>,
    check: <path d="m5 12 4 4L19 6" />,
    plus: <path d="M12 5v14M5 12h14" />,
    grid: <><rect x="4" y="4" width="6" height="6" rx="1"/><rect x="14" y="4" width="6" height="6" rx="1"/><rect x="4" y="14" width="6" height="6" rx="1"/><rect x="14" y="14" width="6" height="6" rx="1"/></>,
    clock: <><circle cx="12" cy="12" r="8"/><path d="M12 7v5l3 2"/></>,
    logout: <><path d="M9 4H4v16h5M10 12h10m-4-4 4 4-4 4"/></>,
    eye: <><path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/></>,
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{paths[name] || paths.arrow}</svg>;
}

export default function Brand() {
  return <Link to="/" className="brand" aria-label="CareerLens home">
    <span className="brand-mark" aria-hidden="true"><span /></span>
    <span>career<span className="brand-light">lens</span><sup>•</sup></span>
  </Link>;
}

export function PublicNav() {
  return <header className="public-nav container">
    <Brand />
    <nav aria-label="Main navigation"><Link to="/sample" className="nav-text">Explore a report</Link><Link to="/login" className="nav-text">Log in</Link><Link to="/signup" className="button button-small">Start an analysis <Icon size={16}/></Link></nav>
  </header>;
}

export function Footer() {
  return <footer className="site-footer container"><Brand/><p>A little more clarity. A better next step.</p><span className="eyebrow">Built for the next chapter.</span></footer>;
}
