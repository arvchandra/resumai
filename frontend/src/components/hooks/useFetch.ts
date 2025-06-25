import { useEffect, useState } from 'react';

export default function useFetch(fetchFn: () => any) {
  const [fetchedData, setFetchedData] = useState(null);
  const [isFetching, setIsFetching] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    async function fetchData() {
      setIsFetching(true);

      await new Promise((resolve) => setTimeout(resolve, 1000));

      try {
        const data = await fetchFn();
        setFetchedData(data);
      }
      catch(error) {
        if (error instanceof Error) {
          setError(error.message);
        } else {
          setError('An error occured while fetching data.');
        }
      }

      setIsFetching(false);
    }
    
    fetchData();
  }, [fetchFn]);

  return {
    fetchedData,
    isFetching,
    error
  }
}
