import React from "react";
import TailoredTableRow from "../TailoredResumeTableRow/TailoredResumeTableRow";
import TailoredTableHeadItem from "../TailoredResumeTableHeadItem/TailoredResumeTableHeadItem";

const TailoredResumeTable = ({ theadData, tbodyData, customClass }) => {
    return (
        <table className={customClass}>
            <thead>
                <tr>
                    {theadData.map((h) => {
                        return <TailoredTableHeadItem key={h} item={h}/>;
                    })}
                </tr>
            </thead>
            <tbody>
                {tbodyData.map((item)=> {
                    return <TailoredTableRow key={item.id} data={item.items} />;
                })}
            </tbody>
        </table>
    );
};

export default TailoredResumeTable;