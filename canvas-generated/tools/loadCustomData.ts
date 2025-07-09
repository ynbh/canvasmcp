
import { tool } from "ai";
import { loadCustomDataDataSchema } from "./aitm.schema.ts";
import { loadCustomData, LoadCustomDataData } from "..";

export default tool({
  description: `
  Load custom data
Load custom user data.

Arbitrary JSON data can be stored for a User.  This API
call
retrieves that data for a (optional) given scope.
See {api:UsersController#set_custom_data
Store Custom Data} for details and
examples.

On success, this endpoint returns an object containing
the data that was requested.

Responds with status code 400 if the namespace parameter, +ns+, is
missing or invalid,
or if the specified scope does not contain any data.
    `,
  parameters: loadCustomDataDataSchema.omit({ url: true }),
  execute: async (args : Omit<LoadCustomDataData, "url"> ) => {
    try {
      const { data } = await loadCustomData(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    