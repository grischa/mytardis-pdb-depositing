from django.template import Context
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.views.decorators.cache import never_cache

from tardis.tardis_portal.auth import decorators as authz
from tardis.tardis_portal.shortcuts import render_response_index
from tardis.tardis_portal.models.datafile import Dataset_File


def _collect_data(dataset_file_id):

    def add_to_data(name, value, data, force_list=False):
        if name not in data:
            data[name] = [value] if force_list else value
        elif type(data[name]) == list:
            data[name].append(value)
        else:
            existing_value = data[name]
            data[name] = [existing_value, value]

    data = {}

    # data metadata
    datafile = Dataset_File.objects.get(id=dataset_file_id)
    dfpsets = datafile.datafileparameterset_set.all()
    for dfpset in dfpsets:
        for dfp in dfpset.datafileparameter_set.all():
            add_to_data(dfp.name.name, dfp.get(), data)
    dataset = datafile.dataset
    dspsets = dataset.datasetparameterset_set.all()
    for dspset in dspsets:
        for dsp in dspset.datasetparameter_set.all():
            add_to_data(dsp.name.name, dsp.get(), data)
    experiments = dataset.experiments.all()
    for experiment in experiments:
        epsets = experiment.experimentparameterset_set.all()
        for epset in epsets:
            for ep in epset.experimentparameter_set.all():
                add_to_data(ep.name.name, ep.get(), data)
        # owner data
        for owner in experiment.get_owners():
            owner = {"email": owner.email,
                     "first_name": owner.first_name,
                     "last_name": owner.last_name,
                 }
            add_to_data("contact_authors", owner, data, True)
        # authors data
        for author in experiment.author_experiment_set.all():
            split_author = author.author.strip().split()
            try:
                formatted_author = "%s, %s." % (
                    split_author[-1],
                    ".".join([n[0] for n in split_author[0:-1]])
                )
            except:
                formatted_author = author.author
            add_to_data("authors", formatted_author, data, True)
    return data


@never_cache
@authz.datafile_access_required
def view(request, dataset_file_id):
    prefill = _collect_data(dataset_file_id)
    author_infor = render_to_string("pdb_depositing/author-infor.text",
                                    prefill)
    print prefill.keys()
    context = Context({"dataset_file_id": dataset_file_id,
                       "author_infor": author_infor,
                   })
    return HttpResponse(render_response_index(
        request,
        "pdb_depositing/index.html",
        context))


def download(request, dataset_file_id):
    prefill = _collect_data(dataset_file_id)
    response = HttpResponse(
        render_to_string(
            "pdb_depositing/author-infor.text",
            prefill),
        content_type='text/plain'
    )
    response['Content-Disposition'
    ] = 'attachment; filename="author-infor.text"'
    return response

