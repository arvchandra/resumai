import React from "react";

const TailoredTableRow = ({ data }) => {
    return (
       <tr>
            {data.map((item) => {
                return <td key={item}>{item}</td>
            })}
       </tr>
    );
};

export default TailoredTableRow;