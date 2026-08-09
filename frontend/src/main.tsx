import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

import { RepositoryProvider } from "./context/RepositoryContext";

createRoot(document.getElementById("root")!).render(

    <RepositoryProvider>

        <App />

    </RepositoryProvider>

);
