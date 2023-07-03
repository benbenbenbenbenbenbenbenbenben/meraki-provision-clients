// Give Json Data and numbner of rows to display
// build a table with pagination

function buildTableWithPagination(jsonData, rowsPerPage) {
    var currentPage = 1; // Current page number
    var totalPages = Math.ceil(jsonData.length / rowsPerPage);
  
    var tableBody = document.getElementById('tableBody');
    var paginationContainer = document.getElementById('pagination');
  
    // Initial setup
    updateTable();
    generatePaginationLinks();
  
    function updateTable() {
      var startIndex = (currentPage - 1) * rowsPerPage;
      var endIndex = startIndex + rowsPerPage;
      var pageData = jsonData.slice(startIndex, endIndex);
  
      // Clear existing rows
      tableBody.innerHTML = '';
  
      // Generate HTML for table rows using the data
      for (var i = 0; i < pageData.length; i++) {
        var row = pageData[i];
        var html = '<tr><td>' + (startIndex+i+1) + '</td><td>' + row.name + '</td><td>' + row.mac + '</td></tr>';
        tableBody.innerHTML += html;
      }
    }
  
    function generatePaginationLinks() {
    paginationContainer.innerHTML = ''; // Clear existing links
  
    var startPage = Math.max(1, currentPage - 3);
    var endPage = Math.min(startPage + 6, totalPages);
  
    var prevButton = createPaginationLink('Previous', currentPage > 1 ? currentPage - 1 : null);
    paginationContainer.appendChild(prevButton);
  
    if (startPage > 1) {
      var firstPageLink = createPaginationLink(1, 1);
      paginationContainer.appendChild(firstPageLink);
  
      if (startPage > 2) {
        var ellipsis = document.createElement('span');
        ellipsis.textContent = '...';
        paginationContainer.appendChild(ellipsis);
      }
    }
  
    for (var i = startPage; i <= endPage; i++) {
      var link = createPaginationLink(i, i === currentPage ? null : i);
      paginationContainer.appendChild(link);
    }
  
    if (endPage < totalPages) {
      if (endPage < totalPages - 1) {
        var ellipsis = document.createElement('span');
        ellipsis.textContent = '...';
        paginationContainer.appendChild(ellipsis);
      }
  
      var lastPageLink = createPaginationLink(totalPages, totalPages);
      paginationContainer.appendChild(lastPageLink);
    }
  
    var nextButton = createPaginationLink('Next', currentPage < totalPages ? currentPage + 1 : null);
    paginationContainer.appendChild(nextButton);
  
  }
  
  function createPaginationLink(text, pageNumber) {
    var link = document.createElement('a');
    link.classList.add('page-link')
    link.href = '#/';
    link.textContent = text;
  
    if (pageNumber) {
      link.addEventListener('click', function () {
        currentPage = pageNumber;
        updateTable();
        generatePaginationLinks();
      });
    } else {
      link.classList.add('disabled');
    }
  
    var listItem = document.createElement('li');
    listItem.classList.add('page-item')
    listItem.appendChild(link);
  
    return listItem;
  }
  
}