
import { tool } from "ai";
import { createLinkOutcomeGlobalDataSchema } from "./aitm.schema.ts";
import { createLinkOutcomeGlobal, CreateLinkOutcomeGlobalData } from "..";

export default tool({
  description: `
  Create/link an outcome
Link an outcome into the outcome group. The outcome to link can either
be
specified by a PUT to the link URL for a specific outcome (the outcome_id
in the PUT URLs) or by
supplying the information for a new outcome (title,
description, ratings, mastery_points) in a POST
to the collection.

If linking an existing outcome, the outcome_id must identify an
outcome
available to this context; i.e. an outcome owned by this group's context,
an outcome owned
by an associated account, or a global outcome. With
outcome_id present, any other parameters (except
move_from) are ignored.

If defining a new outcome, the outcome is created in the outcome
group's
context using the provided title, description, ratings, and mastery points;
the title is
required but all other fields are optional. The new outcome
is then linked into the outcome
group.

If ratings are provided when creating a new outcome, an embedded rubric
criterion is
included in the new outcome. This criterion's mastery_points
default to the maximum points in the
highest rating if not specified in the
mastery_points parameter. Any ratings lacking a description
are given a
default of "No description". Any ratings lacking a point value are given a
default of 0.
If no ratings are provided, the mastery_points parameter is
ignored.
    `,
  parameters: createLinkOutcomeGlobalDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateLinkOutcomeGlobalData, "url"> ) => {
    try {
      const { data } = await createLinkOutcomeGlobal(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    