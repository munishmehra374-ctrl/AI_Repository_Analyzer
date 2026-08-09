import {
    createContext,
    useContext,
    useState,
    ReactNode,
} from "react";

import type{ RepositoryProfile } from "../types/repository";

interface RepositoryContextType {

    taskId: string;

    repositoryProfile: RepositoryProfile | null;

    setTaskId: (taskId: string) => void;

    setRepositoryProfile: (
        profile: RepositoryProfile
    ) => void;

}

const RepositoryContext = createContext<
    RepositoryContextType | undefined
>(undefined);

export function RepositoryProvider({

    children,

}: {
    children: ReactNode;
}) {

    const [taskId, setTaskId] = useState("");

    const [repositoryProfile, setRepositoryProfile] =
        useState<RepositoryProfile | null>(null);

    return (

        <RepositoryContext.Provider
            value={{
                taskId,
                repositoryProfile,
                setTaskId,
                setRepositoryProfile,
            }}
        >

            {children}

        </RepositoryContext.Provider>

    );

}

export function useRepository() {

    const context = useContext(
        RepositoryContext
    );

    if (!context) {

        throw new Error(
            "useRepository must be used inside RepositoryProvider"
        );

    }

    return context;

}