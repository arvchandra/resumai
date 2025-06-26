import React, { createContext, useContext, useState } from 'react';

import type User from '../../interfaces/User';

export interface UsersContextType {
  users: User[];
  setUsers: (users: User[]) => void;
}

export const UsersContext = createContext<UsersContextType>({
  users: [], 
  setUsers: () => {}
});

export const UsersContextProvider = ({ children }: { children: React.ReactNode}) => {
  const [users, setUsers] = useState<User[]>([]);

  const ctxValue = {
    users,
    setUsers,
  }

  return <UsersContext.Provider value={ctxValue}>
    { children }
  </UsersContext.Provider>
}

export const useUsersContext = (): UsersContextType => {
  const ctx = useContext(UsersContext);
  return ctx;
}

