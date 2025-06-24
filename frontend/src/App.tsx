import { useCallback } from "react";

import SearchableDropdown from "./components/SearchableDropdown";
import SortableUsersTable from "./components/SortableUsersTable";
import UsersDropdown from "./components/UsersDropdown";

import "./App.css";
import "./assets/styles/shared.css";

import type User from "./interfaces/User";

import { usersData, usersDataAlt, usersTableData } from "./mocks/mockData";

function App() {
  const handleUserSelect = useCallback((user: User) => {
    alert(`Selected: ${user.name}`);
  }, []);

  return (
    <div className="App">
      <UsersDropdown id="usersSelect" users={usersData} />
      <UsersDropdown id="usersSelectAlt" users={usersDataAlt} />
      <SearchableDropdown id="searchableUsersSelect" items={usersData} />
      <SortableUsersTable users={usersTableData} handleUserSelect={handleUserSelect} />
    </div>
  );
}

export default App;
