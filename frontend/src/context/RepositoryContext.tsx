import {
    createContext,
    useContext,
    useState,
    type ReactNode,
} from "react";

import type { RepositoryProfile } from "../types/repository";

interface RepositoryContextType {

    taskId: string;

    repositoryId: string;

    repositoryProfile: RepositoryProfile | null;

    setTaskId: (taskId: string) => void;

    setRepositoryId: (
        repositoryId: string
    ) => void;

    setRepositoryProfile: (
        profile: RepositoryProfile
    ) => void;
}

const RepositoryContext = createContext<
    RepositoryContextType | undefined
>(undefined);

const TASK_ID_KEY = "repository_task_id";
const REPOSITORY_ID_KEY = "repository_id";
const REPOSITORY_PROFILE_KEY = "repository_profile";

export function RepositoryProvider({
    children,
}: {
    children: ReactNode;
}) {

    const [taskId, setTaskIdState] = useState<string>(() => {

        return localStorage.getItem(
            TASK_ID_KEY
        ) || "";
    });

    const [repositoryId, setRepositoryIdState] =
        useState<string>(() => {

            return localStorage.getItem(
                REPOSITORY_ID_KEY
            ) || "";
        });

    const [repositoryProfile, setRepositoryProfileState] =
        useState<RepositoryProfile | null>(() => {

            const saved = localStorage.getItem(
                REPOSITORY_PROFILE_KEY
            );

            if (!saved) {
                return null;
            }

            try {
                return JSON.parse(saved);
            } catch {
                return null;
            }
        });

    const setTaskId = (id: string) => {

        setTaskIdState(id);

        localStorage.setItem(
            TASK_ID_KEY,
            id
        );

        localStorage.setItem(
            "task_id",
            id
        );
    };

    const setRepositoryId = (
        id: string
    ) => {

        setRepositoryIdState(id);

        localStorage.setItem(
            REPOSITORY_ID_KEY,
            id
        );
    };

    const setRepositoryProfile = (
        profile: RepositoryProfile
    ) => {

        setRepositoryProfileState(profile);

        localStorage.setItem(
            REPOSITORY_PROFILE_KEY,
            JSON.stringify(profile)
        );
    };

    return (

        <RepositoryContext.Provider
            value={{
                taskId,
                repositoryId,
                repositoryProfile,
                setTaskId,
                setRepositoryId,
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