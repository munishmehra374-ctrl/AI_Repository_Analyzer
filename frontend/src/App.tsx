import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import UploadRepository from "./pages/UploadRepository/UploadRepository";
import Indexing from "./pages/Indexing/Indexing";

import Dashboard from "./pages/Dashboard/Dashboard";
import Chat from "./pages/Chat/Chat";
import Analysis from "./pages/Analysis/Analysis";

import MainLayout from "./layouts/MainLayout";

function App() {

    return (

        <BrowserRouter>

            <Routes>

                <Route
                    path="/"
                    element={<UploadRepository />}
                />

                <Route
                    path="/indexing"
                    element={<Indexing />}
                />

                <Route element={<MainLayout />}>

                    <Route
                        path="/dashboard"
                        element={<Dashboard />}
                    />

                    <Route
                        path="/chat"
                        element={<Chat />}
                    />

                    <Route
                        path="/analysis"
                        element={<Analysis />}
                    />

                </Route>

                <Route
                    path="*"
                    element={<Navigate to="/" />}
                />

            </Routes>

        </BrowserRouter>

    );
}

export default App;