//- ----------------------------------
//- 💥 DISPLACY ENT
//- ----------------------------------

'use strict';

class displaCyENT {
    constructor (api, options) {
        this.api = api;
        this.container = document.querySelector(options.container || '#displacy');

        this.defaultText = options.defaultText || 'When Sebastian Thrun started working on self-driving cars at Google in 2007, few people outside of the company took him seriously.';
        this.defaultModel = options.defaultModel || 'en';
        this.defaultEnts = options.defaultEnts || ['person', 'org', 'gpe', 'loc', 'product','grape'];

        this.onStart = options.onStart || false;
        this.onSuccess = options.onSuccess || false;
        this.onError = options.onError || false;
        this.onRender = options.onRender || false;
        this.csrftoken = options.csrftoken;
    }

    parse(text = this.defaultText, model = this.defaultModel, ents = this.defaultEnts) {
        if(typeof this.onStart === 'function') this.onStart();

        let xhr = new XMLHttpRequest();
        xhr.open('POST', this.api, true);
        xhr.setRequestHeader('Content-type', 'text/plain');
        xhr.setRequestHeader("X-CSRFToken", this.csrftoken);
        xhr.onreadystatechange = () => {
            if(xhr.readyState === 4 && xhr.status === 200) {
                if(typeof this.onSuccess === 'function') this.onSuccess();
                this.render(text, JSON.parse(xhr.responseText), ents);
            }

            else if(xhr.status !== 200) {
                if(typeof this.onError === 'function') this.onError(xhr.statusText);
            }
        }

        xhr.onerror = () => {
            xhr.abort();
            if(typeof this.onError === 'function') this.onError();
        }

        xhr.send(JSON.stringify({ text, model }));
    }

    render(text, spans, ents) {
        this.container.innerHTML = '';
        let offset = 0;
        
        //console.log(spans.ents)
        //spans = [{"start":0,"end":18,"label":"GRAPE"}]
        
        spans.ents.forEach(({ label, start, end }) => {
            const entity = text.slice(start, end);
            const fragments = text.slice(offset, start).split('\n');
 
            fragments.forEach((fragment, i) => {
                //this.container.appendChild(document.createTextNode(fragment));
                if(fragments.length > 1 && i != fragments.length - 1) 
                    this.container.appendChild(document.createElement('br'));
                else{
                    const span = document.createElement('span');
                    span.setAttribute('id','1')
                    span.appendChild(document.createTextNode(fragment))
                    this.container.appendChild(span);
                }
            });

            if(ents.includes(label.toLowerCase())) {
                const mark = document.createElement('mark');
                mark.setAttribute('data-entity', label.toLowerCase());
                mark.appendChild(document.createTextNode(entity));
                this.container.appendChild(mark);
            }

            else {
                this.container.appendChild(document.createTextNode(entity));
            }

            offset = end;
        });
        
        this.container.appendChild(document.createTextNode(text.slice(offset, text.length)));
        
        console.log(`%c💥  HTML markup\n%c<div class="entities">${this.container.innerHTML}</div>`, 'font: bold 16px/2 arial, sans-serif', 'font: 13px/1.5 Consolas, "Andale Mono", Menlo, Monaco, Courier, monospace');

        if(typeof this.onRender === 'function') this.onRender();
    }
}
