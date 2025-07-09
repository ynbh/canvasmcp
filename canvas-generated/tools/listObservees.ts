
import { tool } from "ai";
import { listObserveesDataSchema } from "./aitm.schema.ts";
import { listObservees, ListObserveesData } from "..";

export default tool({
  description: `
  List observees
A paginated list of the users that the given user is observing.

*Note:* all users
are allowed to list their own observees. Administrators can list
other users' observees.

The
returned observees will include an attribute "observation_link_root_account_ids", a list
of ids for
the root accounts the observer and observee are linked on. The observer will only be able to
observe
in courses associated with these root accounts.
    `,
  parameters: listObserveesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListObserveesData, "url"> ) => {
    try {
      const { data } = await listObservees(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    