# Element customization

For the POC, we will modify the Element webapp to merge MXIDs of a unique user. Although it's definitely not production ready, here's the steps that have been implemented.

## Setup web-element dev env

<https://github.com/element-hq/element-web#setting-up-a-dev-environment>

In a new folder checkout these following versions :

- js-sdk: `30.1.0` <https://github.com/matrix-org/matrix-js-sdk/tree/v30.1.0>
- react-sdk: `3.85.0` <https://github.com/matrix-org/matrix-react-sdk/tree/v3.85.0>
- element-web: `1.11.50` <https://github.com/element-hq/element-web/tree/v1.11.50>

## patch project

The following patches:

- `./js-sdk/eimis-member-merge_js-sdk.patch`
- `./react-sdk/eimis-member-merger_react-sdk.patch`

- introduce a eimisMemberMerger service :
  - load users and their linked MXIDs at startup
  - make a room member merge function available
- change some parts of the interfaces where relevant:
  - room member count
  - room member info panel

⚠ Very far from being production ready, this is just to be archived somewhere.