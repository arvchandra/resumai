import { useEffect, useState } from "react";

export default function useFetch(fetchFn, initialValue) {
  const [fetchedData, setFetchedData] = useState(initialValue);
  const [isFetching, setIsFetching] = useState(false);
  const [error, setError] = useState();

  useEffect(() => {
    async function fetchData() {
      setIsFetching(true);
      await new Promise((resolve) => setTimeout(resolve, 1000));
      try {
        const data = await fetchFn();
        setFetchedData(data);
      } catch (error) {
        setError({ message: error });
      }
      setIsFetching(false);
    }

    fetchData();
  }, [fetchFn]);

  return {
    fetchedData,
    isFetching,
    error,
  };
}