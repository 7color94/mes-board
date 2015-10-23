function my_function(toUser) {
    content = $("#board-text");
    oldContent = content.val();
    prefix = toUser + "@";
    newContent = '';
    if(oldContent.length > 0){
        if (oldContent != prefix) {
            newContent =  prefix + oldContent;
        }
    } else {
        newContent = prefix;
    }
    content.focus();
    content.val(newContent);
}