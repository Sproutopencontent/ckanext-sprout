"use strict";
this.ckan.module('sprout_answer_question', function ($) {
    
    

    function post(action, data) {
        var api_ver = 3;
        var base_url = ckan.sandbox().client.endpoint;
        var url = base_url + '/api/' + api_ver + '/action/' + action;
        return $.post(url, data, 'json');

    }
    function initialize() {
        var numResources = this.options.num_resources
        console.log(numResources)
        var resource_id = this.options.resource_id
        console.log(resource_id)
        var elementId = '#button-answer_questions-' + resource_id
        $(elementId).on("click", function(e){
            postApiCall($(elementId), resource_id)
        });
    }

    return {
        initialize: initialize
    }

    function postApiCall(saveButton, resource_id) {
        console.log(resource_id)      
        var inputs
        var data = [] // List of Json objects
        
        inputs = saveButton.parents('.modal-content').children('.modal-body').children('.form-group').each( function(){
            var obj = new Object() //create New Object
            obj.question = $(this).children('label').text()
            obj.answer = $(this).children('.controls').children('input').val()
            data.push(obj)

        })
        var data_dict = { data, resource_id }
        console.log(data_dict)
        post('answer_questions', JSON.stringify(data_dict))
        // zemam parent od veke select button i tuka samo questions
        // questions = document.getElementsByName('question');
        // var data = []
        // var data_dict = {data} //json object with list of json objects
        // questions.forEach(element => getQuestionsAnswers(element, data_dict))
        // console.log(JSON.stringify(data_dict))

        // post('answer_questions', JSON.stringify(data_dict))
    }

});
