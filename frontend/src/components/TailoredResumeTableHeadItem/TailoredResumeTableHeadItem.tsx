import React from "react";

const TailoredTableHeadItem = ({ item }) => {
    return (
        <td title={item}>
            {item}
        </td>
    );
};

export default TailoredTableHeadItem;