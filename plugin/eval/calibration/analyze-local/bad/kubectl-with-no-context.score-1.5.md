# Diagnostic — Container Trouble

User has a container that won't come up.

## Investigation

Ran `kubectl get pods` to see the state:

```
$ kubectl get pods
No resources found in default namespace.
```

Tried `kubectl describe`:

```
$ kubectl describe pod api
Error from server (NotFound): pods "api" not found
```

The pod doesn't seem to exist. Maybe it's a deployment issue or a namespace issue.

## Recommendations

- Check the deployment manifest
- Verify the namespace
- Make sure the cluster context is set correctly
- Try `kubectl apply -f deployment.yml` again

## Conclusion

Could not find the failing container. The user should double-check the kubectl setup before running this again.
