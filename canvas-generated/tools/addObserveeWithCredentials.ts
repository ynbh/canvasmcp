
import { tool } from "ai";
import { addObserveeWithCredentialsDataSchema } from "./aitm.schema.ts";
import { addObserveeWithCredentials, AddObserveeWithCredentialsData } from "..";

export default tool({
  description: `
  Add an observee with credentials
Register the given user to observe another user, given the
observee's credentials.

*Note:* all users are allowed to add their own observees, given the
observee's
credentials or access token are provided. Administrators can add observees given
credentials, access token or
the {api:UserObserveesController#update observee's id}.
    `,
  parameters: addObserveeWithCredentialsDataSchema.omit({ url: true }),
  execute: async (args : Omit<AddObserveeWithCredentialsData, "url"> ) => {
    try {
      const { data } = await addObserveeWithCredentials(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    