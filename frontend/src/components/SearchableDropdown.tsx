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

    if (inputValue !== '') {
      setShowDropdown(true);
    } else {
      setShowDropdown(false);
    }
  }

  // Sort the dropdown items initially
  const sortedItems = useMemo(() => {
    return [...items].sort((a, b) => sortNamesFunction(a.name, b.name));
  }, [items]);

  // Filter the dropdown items based on the search term (case-insensitive)
  const filteredItems = sortedItems.filter((item) => {
    if (searchTerm.trim() !== '') {
      return item.name.toLowerCase().includes(searchTerm.trim().toLowerCase());
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

  return (
    <div className="dropdown-container">
      <label htmlFor={searchInputId}>Select item:</label>
      <input id={searchInputId} type="text" onChange={handleSearchTermChange} value={searchTerm} />
      {showDropdown && (
          <ul>
            {
              filteredItems.length > 0 ? (
                filteredItems.map((item) => {
                  return <li key={item.id} value={item.id} onClick={() => handleItemSelect(item.id)}>
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