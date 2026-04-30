# Spike — Kubernetes adoption

## Question

Should we migrate to Kubernetes?

## Findings

Kubernetes is the industry standard for containerization. Every tech company uses it. It's more powerful than our current setup.

We should build a Kubernetes cluster. It will make deployments better.

## Effort

Probably 6-8 weeks. Could be less if we use a managed service.

## Risks

None really. It's just a different deployment target.

## Recommendation

Yes, let's build it.

## Notes

Have not measured current deployment latency. Don't know what our actual bottlenecks are. Did not compare with managed services (AWS EKS, GKE, etc.). Did not research actual time requirements.

Current setup is working fine; don't know if Kubernetes would improve anything for our use case.
