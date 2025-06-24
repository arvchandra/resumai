export const sortNamesFunction = (a: string, b: string) => {
  const lowercaseA = a.toLowerCase();
  const lowercaseB = b.toLowerCase();

  if (lowercaseA < lowercaseB) {
    return -1;
  }
  if (lowercaseA > lowercaseB) {
    return 1;
  }
  
  return 0;
}