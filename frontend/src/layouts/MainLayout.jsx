import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import './MainLayout.css';

export default function MainLayout({ children }) {
    return (
        <div className="layout">
            <Navbar />
            <main className="layout__main">{children}</main>
            <Footer />
        </div>
    );
}
