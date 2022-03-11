# Introduction

Layered Event Data Model and services.

## Development

* [x] Get simple Awkward Array working
* [x] Get simple ServiceX working
* [x] Get simple nested dataset working
* [ ] Add sub-objects (like a 4 vector object)
* [ ] Add behaviors for objects in the awk version (like jets) and the nested version
* [ ] Add filter at dataset level (e.g. events)
* [ ] Add filter at object level (e.g. jets)
* [ ] Typing
* [ ] Caching

## Goals

Write something like this for servicex:

```python
class jet:
    @property
    @ledm.remap(lambda j: j.pt())
    def px(self) -> float:
        ...
    
    @property
    @ledm.remap(lambda j: j.pz())
    def pz(self) -> float:
        ...

@ledm.sx_layer
class evt:
    @property
    @ledm.remap(lambda e: e.Jets())
    def jets(self) -> Iterable[jet]:
        ...
```

With this one can write:

```python
ds = ServiceXDataset('mc16.zee)

events = evt(ds)
jet_pt = events.jets.pz
```

and `jet_pt` will be `ObjectStream`, by events, of all jet `pt`'s, as single column. If one were to write `events.jets` then one would get back records with `pt` and `pz` as fields. Applying `.value()` or similar would get the thing rendered properly.

One can also wrap and filter (and add new fields)

```python
@ledm.sx_layer
@ledm.filter(lambda e: [j for j in e.jets() if j.pt > 3000].Count() == 2])
class preselection:
    @property
    @ledm.remap(lambda e: [j for e.jets if j.pt > 30000)
    def good_jets(self) -> Iterable[jet]:
        ...
```

Then, from above:

```python
ds = ServiceXDataset('mc16.zee)

events = evt(ds)
presel = preselection(events)
```

And you can look at `good_jets` or `jets` for only events that have the reselection cuts applied. Note the nesting of the actions.
