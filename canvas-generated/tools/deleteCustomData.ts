
import { tool } from "ai";
import { deleteCustomDataDataSchema } from "./aitm.schema.ts";
import { deleteCustomData, DeleteCustomDataData } from "..";

export default tool({
  description: `
  Delete custom data
Delete custom user data.

Arbitrary JSON data can be stored for a User.  This API
call
deletes that data for a given scope.  Without a scope, all custom_data is deleted.
See
{api:UsersController#set_custom_data Store Custom Data} for details and
examples of storage and
retrieval.

As an example, we'll store some data, then delete a subset of it.

Example
{api:UsersController#set_custom_data PUT} with valid JSON data:
curl
'https://<canvas>/api/v1/users/<user_id>/custom_data' \
-X PUT \
-F
'ns=com.my-organization.canvas-app' \
-F 'data[fruit][apple]=so tasty' \
-F 'data[fruit][kiwi]=a bit
sour' \
-F 'data[veggies][root][onion]=tear-jerking' \
-H 'Authorization: Bearer
<token>'

Response:
!!!javascript
{
"data": {
"fruit": {
"apple": "so tasty",
"kiwi": "a bit
sour"
},
"veggies": {
"root": {
"onion": "tear-jerking"
}
}
}
}

Example DELETE:
curl
'https://<canvas>/api/v1/users/<user_id>/custom_data/fruit/kiwi' \
-X DELETE \
-F
'ns=com.my-organization.canvas-app' \
-H 'Authorization: Bearer
<token>'

Response:
!!!javascript
{
"data": "a bit sour"
}

Example
{api:UsersController#get_custom_data GET} following the above DELETE:
curl
'https://<canvas>/api/v1/users/<user_id>/custom_data' \
-X GET \
-F
'ns=com.my-organization.canvas-app' \
-H 'Authorization: Bearer
<token>'

Response:
!!!javascript
{
"data": {
"fruit": {
"apple": "so tasty"
},
"veggies": {
"root":
{
"onion": "tear-jerking"
}
}
}
}

Note that hashes left empty after a DELETE will get removed from
the custom_data store.
For example, following the previous commands, if we delete
/custom_data/veggies/root/onion,
then the entire /custom_data/veggies scope will be
removed.

Example DELETE that empties a parent scope:
curl
'https://<canvas>/api/v1/users/<user_id>/custom_data/veggies/root/onion' \
-X DELETE \
-F
'ns=com.my-organization.canvas-app' \
-H 'Authorization: Bearer
<token>'

Response:
!!!javascript
{
"data": "tear-jerking"
}

Example
{api:UsersController#get_custom_data GET} following the above DELETE:
curl
'https://<canvas>/api/v1/users/<user_id>/custom_data' \
-X GET \
-F
'ns=com.my-organization.canvas-app' \
-H 'Authorization: Bearer
<token>'

Response:
!!!javascript
{
"data": {
"fruit": {
"apple": "so tasty"
}
}
}

On success, this
endpoint returns an object containing the data that was deleted.

Responds with status code 400 if
the namespace parameter, +ns+, is missing or invalid,
or if the specified scope does not contain any
data.
    `,
  parameters: deleteCustomDataDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteCustomDataData, "url"> ) => {
    try {
      const { data } = await deleteCustomData(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    