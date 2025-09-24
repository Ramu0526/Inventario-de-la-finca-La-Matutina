(function($){
    $(document).ready(function(){
        var parentTagsSelect = $('#id_etiquetas_padre');
        var subTagsSelect = $('#id_sub_etiquetas');

        function updateSubEtiquetas() {
            var selectedParentIds = parentTagsSelect.val();
            var url = '/admin/get_sub_etiquetas/';

            if (selectedParentIds && selectedParentIds.length > 0) {
                $.ajax({
                    url: url,
                    data: {
                        'parent_ids': selectedParentIds.join(',')
                    },
                    dataType: 'json',
                    success: function(data){
                        var selectedSubTags = subTagsSelect.val();
                        subTagsSelect.empty();
                        $.each(data, function(key, value){
                            var option = $('<option>', {
                                value: key,
                                text: value
                            });
                            if (selectedSubTags && selectedSubTags.includes(String(key))) {
                                option.attr('selected', 'selected');
                            }
                            subTagsSelect.append(option);
                        });
                    }
                });
            } else {
                subTagsSelect.empty();
            }
        }

        $(document).on('change', '#id_etiquetas_padre_to, #id_etiquetas_padre_from', function() {
            setTimeout(updateSubEtiquetas, 100);
        });
        
        // Initial load to populate sub-tags if parent tags are already selected
        if (parentTagsSelect.val() && parentTagsSelect.val().length > 0) {
            updateSubEtiquetas();
        }
    });
})(grp.jQuery);
