$(function() {
    $("#id_open_date").datepicker();
});

$(function() {
  $('label[for=id_incident_description]').after('<small id="help-text" class="form-text text-muted"></small>');
  $('label[for=id_incident_description').after('<small class="form-text text-muted">Questions to ask:</small>');
  
});

$(function() {
    $(":checkbox").change(function() {
        division = $(this).attr('value');
        division_questions = {
            "ACA": ["When was the course taken (year, semester)?",
                "Who taught the course?",
                "Who was the client’s GSI?",
                "What is the course number?",
                "Please describe case with as many details as possible.",
                "Do you have any available documents as evidence (ex: papers, transcripts, notes, forms, etc.)?",
                "Is this case urgent or time sensitive?",
            ],
            "CON": ["Please describe your case and include any pertinent dates, people involved, class and professor, etc..",
                "Were you over the age of 21 at the time of the incident? (For cases involving alcohol.)",
                "Do you have any available documents as evidence (ex. papers, transcripts, notes, forms, etc.?",
                "What is your status with the CSC?",
                "Have you received an AVL (Alleged Violation Letter)?",
                "Have you been told that the case will be forwarded to the CSC?",
                "Is the CSC involved yet?",
                "Are you just seeking advice?",
                "Is this case urgent or time sensitive?",
            ],
            "FIN": ["Please describe case with as many details as possible.",
                "Do you have or can you make any copies of documents such as Financial Aid Awards Summary, Financial Aid Status, emails/letters from the Financial Aid Office, a denial letter from the Residency Office or the Office of the General Counsel?",
                "Have you filled out the FAFSA and, if so, did you do it by the deadline? Did you have any trouble filling out the FAFSA? (If they haven’t filled out the FAFSA, tell them that they still can!)",
                "Do you have any questions regarding the three requirements for establishing residency and whether or not you fulfill them? ",
                "Has any information regarding your financial situation changed (ex. family hardships, drastic additions to expenses, personal finances)? If so, have you filled out a Budget Appeal, a Parent Contribution Appeal, or an Independence Appeal?",
                "Have you talked to any administrators (ex. Cal Student Central, the Financial Aid Office, the Billing and Payments Office, the Residency Affairs Office, or the Office of the Registrar)?",
                "Is this case urgent or time sensitive?",
            ],
            "GRI": ["Can you please provide specific dates, names, as well as a description of the incident you would like to report?",
                "What is the relevant program or office, if there is one?",
                "Can you please name any directors, administrators, or faculty that you have spoken to regarding the incident?",
                "Have you made any attempts at an informal resolution?",
            ]
        }

        if (this.checked) {
            help_text = $('#help-text');
            help_text.append(`<ul id=${division}-questions></ul>`);
            questions_list = help_text.children(`#${division}-questions`);
            division_questions[division].forEach(function (question) {
              questions_list.append(`<li>${question}</li>`)
            });
        } else {
          $('#help-text').children(`#${division}-questions`).remove();
        }
    });
});

function submitIntake(event) {
	if (document.getElementsByClassName("select2-selection__placeholder").length > 0) { // if no referrer selected
		swal({
		  title: 'Are you sure?',
		  text: "You have not recorded how the client heard about the office. Would you like to submit the intake anyway?",
		  type: 'warning',
		  focusCancel: true,
		  showCancelButton: true,
		  confirmButtonColor: '#d33',
		  cancelButtonColor: '#d2d4d6',
		  confirmButtonText: 'Yes, submit it anyway',
		  cancelButtonText: "No, I'll fill that out"

		}).then((result) => (result.value ? document.getElementsByTagName("form")[0].submit() : false));
		return false;
	}
	return true;
  }

