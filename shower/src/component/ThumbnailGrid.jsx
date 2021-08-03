import React from 'react';

function ThumbnailGrid() {
  const items = ["foo", "bar", "hoge"];
  const listItems = items.map(x => <li key={x}>{x}</li>);
  return (
      <div className="ThumbnailGrid">
      <ul>{listItems}</ul>
      </div>
  );
}

export default ThumbnailGrid;