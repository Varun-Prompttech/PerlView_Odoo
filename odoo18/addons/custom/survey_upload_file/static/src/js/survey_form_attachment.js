/** @odoo-module */
import publicWidget from "@web/legacy/js/public/public_widget";
import SurveyPreloadImageMixin from "@survey/js/survey_preload_image_mixin";

publicWidget.registry.SurveyFormUpload = publicWidget.Widget.extend(SurveyPreloadImageMixin, {
    selector: '.o_survey_form',
    events: {
        'change .o_survey_upload_file': '_onFileChange',
    },

    init() {
        this._super(...arguments);
    },

    _onFileChange: function(event) {
        var self = this;
        var inputEl = event.target;  // the specific input field
        var files = inputEl.files;
        var fileNames = [];
        var dataURLs = [];

        // Get the question id from the input name attribute
        var questionId = inputEl.getAttribute('name');

        // Clear any previous data
        inputEl.setAttribute('data-oe-data', '');
        inputEl.setAttribute('data-oe-file_name', '');

        var fileList = document.getElementById(`fileList_${questionId}`);
        if (fileList) fileList.innerHTML = '';

        let filesProcessed = 0;

        for (let i = 0; i < files.length; i++) {
            let reader = new FileReader();

            reader.onload = function(e) {
                let file = files[i];
                let filename = file.name;
                let dataURL = e.target.result.split(',')[1];

                fileNames.push(filename);
                dataURLs.push(dataURL);

                filesProcessed++;
                if (filesProcessed === files.length) {
                    inputEl.setAttribute('data-oe-data', JSON.stringify(dataURLs));
                    inputEl.setAttribute('data-oe-file_name', JSON.stringify(fileNames));

                    // Render file list
                    if (fileList) {
                        let ul = document.createElement('ul');
                        fileNames.forEach(function(name) {
                            let li = document.createElement('li');
                            li.textContent = name;
                            ul.appendChild(li);
                        });
                        fileList.appendChild(ul);

                        // Add Delete All button
                        let deleteBtn = document.createElement('button');
                        deleteBtn.type = 'button';
                        deleteBtn.textContent = 'Delete All';
                        deleteBtn.addEventListener('click', function() {
                            fileList.innerHTML = '';
                            inputEl.setAttribute('data-oe-data', '');
                            inputEl.setAttribute('data-oe-file_name', '');
                            inputEl.value = '';
                        });
                        fileList.appendChild(deleteBtn);
                    }
                }
            };

            reader.readAsDataURL(files[i]);
        }
    },
});

export default publicWidget.registry.SurveyFormUpload;
