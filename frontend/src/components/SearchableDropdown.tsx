import React, { useMemo, useState } from "react";

import { sortNamesFunction } from "../util/sort";

interface Item {
  id: number;
  name: string;
}

interface SearchableDropdownProps {
  id: string;
  items: Item[]
}

const SearchableDropdown: React.FC<SearchableDropdownProps> = ({ id, items }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const [selectedItem, setSelectedItem] = useState<Item>();

  // Construct id for dropdown search input
  const searchInputId = `${id}Input`;

  // Update search term as it is typed
  const handleSearchTermChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const inputValue = event.target.value;
    setSearchTerm(inputValue);

    if (inputValue.trim().length > 0) {
      setShowDropdown(true);
    }
    else {
      setShowDropdown(false);
    }
  }

  // Initial instantiation of alphabetically sorted items
  const sortedItems = useMemo(() => {
    return [...items].sort((a, b) => sortNamesFunction(a.name, b.name));
  }, [items]);

  // Filter the dropdown items based on the search term (case-insensitive)
  const filteredItems = sortedItems.filter((item, index) => {
    if (searchTerm.length > 0) {
      return item.name.toLowerCase().includes(searchTerm.trim().toLowerCase());
    } 

    // For empty search term, return top 5 items
    if (index < 10) {
      return true;
    }
  });

  // Set selected item
  const handleItemSelect = (id: number) => {
    console.log(`New selection: ${selectedItem?.name}`);
    const item = items.find((item) => item.id == id);
    setSelectedItem(item);
    if (item !== undefined) {
      setSearchTerm(item.name);
      setShowDropdown(false);
    }
    console.log(`New selection: ${item?.name}`);
  }

  // Show first 5 users when search bar is focused
  const handleSearchBarFocus = () => {
    setShowDropdown(true);
  }

  // Hide the dropdown if focus is no longer on the search bar
  const handleSearchBarBlur = () => {
    setShowDropdown(false);
  }

  return (
    <div className="dropdown-container">
      <label htmlFor={searchInputId}>Select item:</label>
      <input 
        id={searchInputId} 
        type="search"
        value={searchTerm} 
        onChange={handleSearchTermChange} 
        onFocus={handleSearchBarFocus}
        onBlur={handleSearchBarBlur}
      />
      {showDropdown && (
          <ul>
            {
              filteredItems.length > 0 ? (
                filteredItems.map((item) => {
                  return <li key={item.id} value={item.id} onMouseDown={() => handleItemSelect(item.id)}>
                    {item.name}
                  </li>;
                })
              ) : <li>No results</li>
            }
          </ul>
        )
      }
    </div>
  );
}

export default SearchableDropdown;